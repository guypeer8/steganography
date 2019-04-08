## Steganography
##### Steganography is the art of implanting content in a file, by inserting the underline data in the parent file's least significant bits.

##### Usage:
```js
python3 steganography.py --encode "I know someday you'll have a beautiful life, I know you'll be the sun in somebody else's skys, but whyy! whyy! whyyy... can't it be, oh can't it be mineeeeeee... ahhh"
 
python3 steganography.py --decode 
# returns the underline text: "I know someday you'll have a beautiful life, I know you'll be the sun in somebody else's skys, but whyy! whyy! whyyy... can't it be, oh can't it be mineeeeeee... ahhh"

python3 steganography.py --diff
# returns the dictionary {'pixels': 157920, 'diff': 41} - indicating how far are the 2 images from each other (at most 3 for each tgb cell portion)
```
