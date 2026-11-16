#pragma once
#include <stdbool.h>
#include "digits.h"
static inline bool uses_24(int mode,bool watch24){return mode==2 || (mode==0 && watch24);}
static inline int display_hour(int hour,int mode,bool watch24){return uses_24(mode,watch24)?hour:(hour%12?hour%12:12);}
static inline int pair_left(int value,int panel_x){return panel_x+(87-DIGIT_LEFT[value/10]-38-DIGIT_RIGHT[value%10])/2;}
static inline int battery_bars(int percent){return (percent+24)/25;}
static inline int battery_group_left(int label_width){return (200-(60+label_width))/2;}
