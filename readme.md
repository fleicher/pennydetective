General Structure
=================

1. Edge Detection / increase contrast
2. rotate image
    * information 
    ```
    {
    "Text": "Gilletitas",
      "Geometry": {
        "BoundingBox": {
          "Width": 0.18798895180225372,
          "Height": 0.026904122903943062,
          "Left": 0.13337668776512146,
          "Top": 0.49319759011268616
        },
        "Polygon": [  // the origin in in the top-left corner
          {  // top-left (if the page is rotated)
            "X": 0.1354224681854248,
            "Y": 0.49319759011268616
          },
          {  // top-right
            "X": 0.321365624666214,
            "Y": 0.49886035919189453
          },
          {  // bottom-right
            "X": 0.31931984424591064,
            "Y": 0.5201017260551453
          },
          {  //bottom-left
            "X": 0.13337668776512146,
            "Y": 0.5144389867782593
          }
        ]
      }
    }
     ```
3. Get text from API
4. find/suggest Block where the actual Data + Sum is
5. Read line by line: 
    * Text
    * Number
    * Category
    * (maybe amount line)
6. check if Sum(Data) = Sum, otherwise ask
7. spellchecker on Data. 
8. diff checker with existing data -> categorize 
    * potentially use my own NN here. 