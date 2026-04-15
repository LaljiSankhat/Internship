this model uses Matryoshka Representation Learning 


this is learning techniques where embedding are created in such way that most of the 
accuracy we can achieve with the first fewer dimentions
we can then increase dimention of embedding to get more accuracy 
at max for this model we have 3072 dimetions

in this learning techniques we dont have a single loss funtion for all the dimentions
instead of that we make loss funciton for first 8 dim, then find for 16, 32, 64 , 128, 256, 512 ....

then add all losses to create final loss function 

total Loss = L(8) + L(16) + L(32) + L(64) + L(128) + ...... + L(3072)  -> for embedding 2

this ensures that we can get better results at fewer dimentions.


so we can get beter results at fewer storage capacity.