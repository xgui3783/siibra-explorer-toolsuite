from typing import Optional
from siibra.atlas import Atlas
from siibra.space import Space
from siibra.parcellation import Parcellation
from siibra.region import Region

import math
from .util import encode_number,separator

root_url='https://atlases.ebrains.eu/viewer/'

def sanitize_id(id: str):
    return id.replace('/', ':')

def run(atlas: Atlas, space: Space, parc: Parcellation, region: Optional[Region]):

    nav_string='/@:0.0.0.-W000.._eCwg.2-FUe3._-s_W.2_evlu..7LIx..{encoded_nav}..1LSm'
    return_url='{root_url}#/a:{atlas_id}/t:{template_id}/p:{parc_id}'.format(
        root_url    = root_url,
        atlas_id    = sanitize_id(atlas.id),
        template_id = sanitize_id(space.id),
        parc_id     = sanitize_id(parc.id),
    )
    if region is None:
        return return_url + nav_string.format(encoded_nav='0.0.0')
    
    if len(region.labels) == 0:
        raise IndexError(f'region has no labels. Cannot generate URL')
    
    label=list(region.labels)[0]
    hemisphere='left hemisphere' if 'left' in region.name else 'right hemisphere' if 'right' in region else 'whole brain'
    ng_id=get_ng_id(atlas.id,space.id,parc.id,hemisphere)

    return_url=f'{return_url}/r:{ng_id}::{encode_number(label)}'

    spatialprops=region.spatialprops(space)
    if len(spatialprops) == 0:
        return return_url + nav_string.format(encoded_nav='0.0.0')
    centroid=spatialprops[0].get('centroid_mm')
    print('centroid', centroid)
    encoded_centroid=separator.join([ encode_number(math.floor(val * 1e6)) for val in centroid ])
    return_url=f'{return_url}/@:0.0.0.-W000.._eCwg.2-FUe3._-s_W.2_evlu..7LIx..{encoded_centroid}..1LSm'
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
  }
}

def get_hash(atlas_id: str, t_id: str, parc_id: str, hemisphere: str):
    full_string=f'{atlas_id}{t_id}{parc_id}{hemisphere}'
    return_val=0
    for char in full_string:
        return_val=return_val << 5 - return_val + ord(char)
    return '_' + hex(return_val)[3:]

def get_ng_id(atlas_id: str, t_id: str, parc_id: str, hemisphere: str):
    backwards_key=backwards_compat_dict.get(atlas_id, {}).get(t_id, {}).get(parc_id, {}).get(hemisphere)
    if backwards_key is not None:
        return backwards_key
    return get_hash(atlas_id, t_id, parc_id, hemisphere)