
Properties
==========

* Zoom, Pan, Rotate, Crop
* Settings: height, width, image preview, ratio, background color

Usage
=====

The widget passes options directly through to image following::
    <field name="image_medium" widget="image" options=
        "{      
        'minWidth': 100,
        'minHeight': 100,
        'maxWidth': 800,
        'maxHeight': 600,
        'ratio': 1,
        'plugins':  {
                    'crop': {
                            'minHeight': 50,
                            'minWidth': 50,
                            'maxHeight': 250,
                            'maxWidth': 250,
                            'ratio': 1,
                            }
                    }
        }" />
