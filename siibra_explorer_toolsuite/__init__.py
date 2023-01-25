from typing import Optional
import siibra
from siibra.core import Atlas, Space, Parcellation, Region
from urllib.parse import quote
from numpy import int32
import numpy as np
from siibra import atlases
min_int32=-2_147_483_648
max_int32=2_147_483_647

BIGBRAIN = siibra.spaces['bigbrain']

if siibra.__version__ != "0.3a6":
    print(f"Warning: siibra.__version__ {siibra.__version__} != 0.3a6, this module may not work properly.")

import math
from .util import encode_number,separator

default_root_url='https://atlases.ebrains.eu/viewer/'

def sanitize_id(id: str):
    return id.replace('/', ':')

def get_perspective_zoom(atlas: Atlas, space: Space, parc: Parcellation, region: Optional[Region]):
    if atlas is atlases['rat'] or atlas is atlases['mouse']:
        return 200000
    return 2000000

def get_zoom(atlas: Atlas, space: Space, parc: Parcellation, region: Optional[Region]):
    if atlas is atlases['rat'] or atlas is atlases['mouse']:
        return 35000
    return 350000

supported_prefix = (
  "nifti://",
  "swc://",
  "precomputed://",
)

def run(atlas: Atlas, space: Space, parc: Parcellation, region: Optional[Region]=None, *, root_url=default_root_url, external_url:str=None, ignore_warning=False):

    overlay_url = None
    if external_url:
        assert any([external_url.startswith(prefix) for prefix in supported_prefix]), f"url needs to start with {(' , '.join(supported_prefix))}"
        overlay_url = '/x-overlay-layer:{url}'.format(
            url=external_url.replace("/", "%2F")
        )

    zoom = get_zoom(atlas, space, parc, region)
    pzoom = get_perspective_zoom(atlas, space, parc, region)
    
    zoom_kwargs = {
        "encoded_pzoom": encode_number(pzoom, False),
        "encoded_zoom": encode_number(zoom, False)
    }
    nav_string='/@:0.0.0.-W000.._eCwg.2-FUe3._-s_W.2_evlu..{encoded_pzoom}..{encoded_nav}..{encoded_zoom}'

    return_url='{root_url}#/a:{atlas_id}/t:{template_id}/p:{parc_id}{overlay_url}'.format(
        root_url    = root_url,
        atlas_id    = sanitize_id(atlas.id),
        template_id = sanitize_id(space.id),
        parc_id     = sanitize_id(parc.id),
        overlay_url = overlay_url if overlay_url else "",
    )
    if region is None:
        return return_url + nav_string.format(encoded_nav='0.0.0', **zoom_kwargs)
    
    hemisphere='left hemisphere' if 'left' in region.name else 'right hemisphere' if 'right' in region.name else 'whole brain'

    if space is BIGBRAIN:
        voi = [v for v in region.volumes if v.space is BIGBRAIN]
        assert len(voi) == 1, f"For big brain volumes, there must be 1 and only 1 region.volumes in big space"
        hemisphere = voi[0].id
        label = voi[0].detail.get("neuroglancer/precomputed", {}).get("labelIndex")
        if label is None:
            raise Exception(f"big brain cannot determine label index")
    else:
        if len(region.labels) == 0:
            raise IndexError(f'region has no labels. Cannot generate URL')
        label=list(region.labels)[0]

    ng_id=get_ng_id(atlas.id,space.id,parc.id,hemisphere)

    return_url=f'{return_url}/r:{quote(ng_id)}::{encode_number(label)}'

    try:
        result_props=region.spatial_props(space)
        result_props_components =result_props.get('components', [])
        if len(result_props_components) == 0:
            return return_url + nav_string.format(encoded_nav='0.0.0', **zoom_kwargs)
    except Exception as e:
        print(f'Cannot get_spatial_props {str(e)}')
        if not ignore_warning:
            raise e
        return return_url + nav_string.format(encoded_nav='0.0.0', **zoom_kwargs)

    centroid=result_props_components[0].get('centroid')
    print('centroid', region, centroid)

    encoded_centroid=separator.join([ encode_number(math.floor(val * 1e6)) for val in centroid ])
    return_url=return_url + nav_string.format(encoded_nav=encoded_centroid, **zoom_kwargs)
    return return_url
    
def main():
    pass

if __name__ == '__main__':
    main()

backwards_compat_dict={

  # human multi level
  'juelich/iav/atlas/v1.0.0/1': {
    # icbm152
    'minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2': {
      # julich brain v2.6
      'minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579-26': {
        'left hemisphere': 'MNI152_V25_LEFT_NG_SPLIT_HEMISPHERE',
        'right hemisphere': 'MNI152_V25_RIGHT_NG_SPLIT_HEMISPHERE'
      },
      # bundle hcp
      # even though hcp, long/short bundle, and difumo has no hemisphere distinctions, the way siibra-python parses the region,
      # and thus attributes left/right hemisphere, still results in some regions being parsed as left/right hemisphere
      "juelich/iav/atlas/v1.0.0/79cbeaa4ee96d5d3dfe2876e9f74b3dc3d3ffb84304fb9b965b1776563a1069c": {
        "whole brain": "superficial-white-bundle-HCP",
        "left hemisphere": "superficial-white-bundle-HCP",
        "right hemisphere": "superficial-white-bundle-HCP"
      },
      # julich brain v1.18
      "minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579": {
        "left hemisphere": "jubrain mni152 v18 left",
        "right hemisphere": "jubrain mni152 v18 right",
      },
      # long bundle
      "juelich/iav/atlas/v1.0.0/5": {
        "whole brain": "fibre bundle long",
        "left hemisphere": "fibre bundle long",
        "right hemisphere": "fibre bundle long",
      },
      # bundle short
      "juelich/iav/atlas/v1.0.0/6": {
        "whole brain": "fibre bundle short",
        "left hemisphere": "fibre bundle short",
        "right hemisphere": "fibre bundle short",
      },
      # difumo 64
      "minds/core/parcellationatlas/v1.0.0/d80fbab2-ce7f-4901-a3a2-3c8ef8a3b721": {
        "whole brain": "DiFuMo Atlas (64 dimensions)",
        "left hemisphere": "DiFuMo Atlas (64 dimensions)",
        "right hemisphere": "DiFuMo Atlas (64 dimensions)",
      },
      "minds/core/parcellationatlas/v1.0.0/73f41e04-b7ee-4301-a828-4b298ad05ab8": {
        "whole brain": "DiFuMo Atlas (128 dimensions)",
        "left hemisphere": "DiFuMo Atlas (128 dimensions)",
        "right hemisphere": "DiFuMo Atlas (128 dimensions)",
      },
      "minds/core/parcellationatlas/v1.0.0/141d510f-0342-4f94-ace7-c97d5f160235": {
        "whole brain": "DiFuMo Atlas (256 dimensions)",
        "left hemisphere": "DiFuMo Atlas (256 dimensions)",
        "right hemisphere": "DiFuMo Atlas (256 dimensions)",
      },
      "minds/core/parcellationatlas/v1.0.0/63b5794f-79a4-4464-8dc1-b32e170f3d16": {
        "whole brain": "DiFuMo Atlas (512 dimensions)",
        "left hemisphere": "DiFuMo Atlas (512 dimensions)",
        "right hemisphere": "DiFuMo Atlas (512 dimensions)",
      },
      "minds/core/parcellationatlas/v1.0.0/12fca5c5-b02c-46ce-ab9f-f12babf4c7e1": {
        "whole brain": "DiFuMo Atlas (1024 dimensions)",
        "left hemisphere": "DiFuMo Atlas (1024 dimensions)",
        "right hemisphere": "DiFuMo Atlas (1024 dimensions)",
      },
    },
    # colin 27
    "minds/core/referencespace/v1.0.0/7f39f7be-445b-47c0-9791-e971c0b6d992": {
      "minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579-26": {
        "left hemisphere": "COLIN_V25_LEFT_NG_SPLIT_HEMISPHERE",
        "right hemisphere": "COLIN_V25_RIGHT_NG_SPLIT_HEMISPHERE",
      },
      "minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579": {
        "left hemisphere": "jubrain colin v18 left",
        "right hemisphere": "jubrain colin v18 right",
      }
    },
    # big brain
    "minds/core/referencespace/v1.0.0/a1655b99-82f1-420f-a3c2-fe80fd4c8588": {
      "minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579-26": {

      },
      # isocortex
      "juelich/iav/atlas/v1.0.0/4": {
        "whole brain": " tissue type: "
      },
      # cortical layers
      "juelich/iav/atlas/v1.0.0/3": {
        "whole brain": "cortical layers"
      },
    },

    # fsaverage
    "minds/core/referencespace/v1.0.0/tmp-fsaverage": {
        "minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579-290": {
            "left hemisphere": "left",
            "right hemisphere": "right"
        }
    },
  },


  # allen mouse
  'juelich/iav/atlas/v1.0.0/2': {
    # ccf v3
    "minds/core/referencespace/v1.0.0/265d32a0-3d84-40a5-926f-bf89f68212b9": {
      # ccf v3 2017
      "minds/core/parcellationatlas/v1.0.0/05655b58-3b6f-49db-b285-64b5a0276f83": {
        "whole brain": "v3_2017",
        "left hemisphere": "v3_2017",
        "right hemisphere": "v3_2017"
      },
      # ccf v3 2015,
      "minds/core/parcellationatlas/v1.0.0/39a1384b-8413-4d27-af8d-22432225401f": {
        "whole brain": "atlas",
        "left hemisphere": "atlas",
        "right hemisphere": "atlas"
      }
    }
  },
  # waxholm
  "minds/core/parcellationatlas/v1.0.0/522b368e-49a3-49fa-88d3-0870a307974a": {
    "minds/core/referencespace/v1.0.0/d5717c4a-0fa1-46e6-918c-b8003069ade8": {
      # v1.01
      "minds/core/parcellationatlas/v1.0.0/11017b35-7056-4593-baad-3934d211daba": {
        "whole brain": "v1_01",
        "left hemisphere": "v1_01",
        "right hemisphere": "v1_01"
      },
      # v2
      "minds/core/parcellationatlas/v1.0.0/2449a7f0-6dd0-4b5a-8f1e-aec0db03679d": {
        "whole brain": "v2",
        "left hemisphere": "v2",
        "right hemisphere": "v2"
      },
      # v3
      "minds/core/parcellationatlas/v1.0.0/ebb923ba-b4d5-4b82-8088-fa9215c2e1fe": {
        "whole brain": "v3",
        "left hemisphere": "v3",
        "right hemisphere": "v3"
      }
    }
  }
}

def get_hash(atlas_id: str, t_id: str, parc_id: str, hemisphere: str):
    full_string=f'{atlas_id}{t_id}{parc_id}{hemisphere}'
    return_val=0
    with np.errstate(over="ignore"):
        for char in full_string:
            # overflowing is expected and in fact the whole reason why convert number to int32
            
            # in windows, int32((0 - min_int32) << 5), rather than overflow to wraper around, raises OverflowError
            shifted_5 = int32(
                (return_val - min_int32) if return_val > max_int32 else return_val
            << 5)

            return_val = int32(shifted_5 - return_val + ord(char))
            return_val = return_val & return_val
    hex_val = hex(return_val)
    val = '_' + hex_val[3:]
    return val

def get_ng_id(atlas_id: str, t_id: str, parc_id: str, hemisphere: str):
    backwards_key=backwards_compat_dict.get(atlas_id, {}).get(t_id, {}).get(parc_id, {}).get(hemisphere)
    if backwards_key is not None:
        return backwards_key
    return get_hash(atlas_id, t_id, parc_id, hemisphere)