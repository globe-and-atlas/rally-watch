#include <pebble.h>
#include "config.h"
#include "policy.h"

enum {P_PALETTE=1,P_BG,P_FG,P_ACCENT,P_TIME,P_DATE};
typedef struct {int palette,bg,fg,accent,time_format,date_format;} Settings;
static Settings s={0,0x000055,0xFFFFAA,0xFF5500,0,1};
static const uint32_t PALETTES[6][3]={
 {0x000055,0xFFFFAA,0xFF5500},{0x000000,0xFFFFFF,0xAA0000},
 {0x005500,0xFFFFFF,0x0055AA},{0x550055,0xFFFFFF,0xAA0055},
 {0x000000,0xAAFFFF,0x0055AA},{0xFFFFFF,0x000000,0xAAAAAA}};
static Window *s_window;
static Layer *s_layer;
static struct tm s_time;
static int s_battery;
#if RALLY_FIXTURE
static int f_hour=RALLY_HOUR,f_minute=RALLY_MINUTE,f_second=RALLY_SECOND,f_battery=RALLY_BATTERY;
#endif
static const char *MONTHS[]={"JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"};
static const char *WEEK[]={"SUN","MON","TUE","WED","THU","FRI","SAT"};
static uint32_t color(int channel) {
 return s.palette<6?PALETTES[s.palette][channel]:(uint32_t)(channel==0?s.bg:channel==1?s.fg:s.accent);
}
static void text(GContext *ctx,const char *value,GFont font,GRect box) {
 graphics_draw_text(ctx,value,font,box,GTextOverflowModeFill,GTextAlignmentCenter,NULL);
}
static void draw_digit(GContext *ctx,int value,int x,int y) {
 const int stride=(DIGIT_WIDTH+7)/8;
 for(int row=0;row<DIGIT_HEIGHT;row++) {
  int start=-1;
  for(int column=0;column<=DIGIT_WIDTH;column++) {
   bool filled=column<DIGIT_WIDTH && (DIGITS[value][row*stride+column/8]&(0x80>>(column%8)));
   if(filled && start<0) start=column;
   if(!filled && start>=0) {graphics_fill_rect(ctx,GRect(x+start,y+row,column-start,1),0,GCornerNone);start=-1;}
  }
 }
}
#if defined(PBL_ROUND)
#include "round_digital.h"
static void round_numeral(GContext *ctx,int value,int x,int y,int w,int h){rmask(ctx,DIGITS[value],DIGIT_WIDTH,DIGIT_HEIGHT,(DIGIT_WIDTH+7)/8,x,y,w,h);}
static void round_current(GContext *ctx){uint32_t bg=color(0),fg=color(1),accent=color(2);RoundData d={0};d.now=s_time;d.bg=bg;d.fg=fg;d.accent=accent;d.battery=s_battery;d.time_mode=s.time_format;d.date_mode=s.date_format;int hour=rhour(&d);d.hour_shift=rpair_shift(DIGITS[hour/10],DIGITS[hour%10],DIGIT_WIDTH,DIGIT_HEIGHT,(DIGIT_WIDTH+7)/8,19,51,29,43,50);d.minute_shift=rpair_shift(DIGITS[d.now.tm_min/10],DIGITS[d.now.tm_min%10],DIGIT_WIDTH,DIGIT_HEIGHT,(DIGIT_WIDTH+7)/8,99,131,29,43,130);round_digital(ctx,&d,7,round_numeral);}
#endif
static void draw(Layer *layer,GContext *ctx) {
#if defined(PBL_ROUND)
 (void)layer;round_current(ctx);rproof_marker(ctx);return;
#endif

 (void)layer;
 graphics_context_set_antialiased(ctx,false);
 graphics_context_set_fill_color(ctx,GColorFromHEX(color(0)));
 graphics_fill_rect(ctx,GRect(0,0,200,228),0,GCornerNone);
 graphics_context_set_fill_color(ctx,GColorFromHEX(color(1)));
 graphics_fill_rect(ctx,GRect(8,32,88,118),6,GCornersAll);
 graphics_context_set_fill_color(ctx,GColorFromHEX(color(2)));
 graphics_fill_rect(ctx,GRect(104,32,88,118),6,GCornersAll);
 int hour=display_hour(s_time.tm_hour,s.time_format,clock_is_24h_style());
 int hour_x=pair_left(hour,8),minute_x=pair_left(s_time.tm_min,104);
 graphics_context_set_fill_color(ctx,GColorFromHEX(color(0)));
 draw_digit(ctx,hour/10,hour_x,43);draw_digit(ctx,hour%10,hour_x+38,43);
 graphics_context_set_text_color(ctx,GColorFromHEX(color(0)));
 text(ctx,"HOUR",fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD),GRect(8,124,88,23));
 graphics_context_set_fill_color(ctx,GColorFromHEX(color(1)));
 draw_digit(ctx,s_time.tm_min/10,minute_x,43);draw_digit(ctx,s_time.tm_min%10,minute_x+38,43);
 graphics_context_set_text_color(ctx,GColorFromHEX(color(1)));
 text(ctx,"MIN",fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD),GRect(104,124,88,23));
 if(!uses_24(s.time_format,clock_is_24h_style()))
  text(ctx,s_time.tm_hour>=12?"PM":"AM",fonts_get_system_font(FONT_KEY_GOTHIC_14_BOLD),GRect(60,8,80,18));
 char date[32]="";
 switch(s.date_format) {
  case 1:snprintf(date,sizeof(date),"%s %s %02d",WEEK[s_time.tm_wday],MONTHS[s_time.tm_mon],s_time.tm_mday);break;
  case 2:snprintf(date,sizeof(date),"%04d-%02d-%02d",s_time.tm_year+1900,s_time.tm_mon+1,s_time.tm_mday);break;
  case 3:snprintf(date,sizeof(date),"%02d/%02d/%04d",s_time.tm_mon+1,s_time.tm_mday,s_time.tm_year+1900);break;
  case 4:snprintf(date,sizeof(date),"%02d/%02d/%04d",s_time.tm_mday,s_time.tm_mon+1,s_time.tm_year+1900);break;
 }
 graphics_context_set_text_color(ctx,GColorFromHEX(color(1)));
 text(ctx,date,fonts_get_system_font(FONT_KEY_GOTHIC_24_BOLD),GRect(9,157,182,30));
 char charge[8];snprintf(charge,sizeof(charge),"%d%%",s_battery);
 GFont font=fonts_get_system_font(FONT_KEY_GOTHIC_24_BOLD);
 GSize size=graphics_text_layout_get_content_size(charge,font,GRect(0,0,60,30),GTextOverflowModeFill,GTextAlignmentLeft);
 int left=battery_group_left(size.w);
 graphics_context_set_stroke_color(ctx,GColorFromHEX(color(1)));
 graphics_context_set_fill_color(ctx,GColorFromHEX(color(1)));
 graphics_context_set_stroke_width(ctx,2);
 graphics_draw_round_rect(ctx,GRect(left,199,44,16),3);
 graphics_fill_rect(ctx,GRect(left+44,204,4,6),1,GCornersAll);
 graphics_context_set_stroke_width(ctx,1);
 for(int i=0;i<battery_bars(s_battery);i++) graphics_fill_rect(ctx,GRect(left+4+i*10,202,7,10),0,GCornerNone);
 text(ctx,charge,font,GRect(left+60,190,size.w+2,32));
}
static void tick(struct tm *now,TimeUnits changed) {
 (void)changed;s_time=*now;
#if RALLY_FIXTURE
 s_time.tm_hour=f_hour;s_time.tm_min=f_minute;s_time.tm_sec=f_second;
 s_time.tm_year=126;s_time.tm_mon=10;s_time.tm_mday=5;s_time.tm_wday=4;
#endif
 layer_mark_dirty(s_layer);
}
static void battery_changed(BatteryChargeState state) {
 s_battery=state.charge_percent;
#if RALLY_FIXTURE
 s_battery=f_battery;
#endif
 layer_mark_dirty(s_layer);
}
static void setting(DictionaryIterator *iter,uint32_t message_key,int persist_key,int maximum,int *target) {
 Tuple *tuple=dict_find(iter,message_key);
 if(!tuple || (tuple->type!=TUPLE_INT && tuple->type!=TUPLE_UINT)) return;
 int value=tuple->value->int32;if(value<0 || value>maximum) return;
 *target=value;persist_write_int(persist_key,value);
}
#if RALLY_FIXTURE
static void fixture_value(DictionaryIterator *iter,int key,int maximum,int *target) {
 Tuple *tuple=dict_find(iter,key);
 if(tuple && tuple->type==TUPLE_INT && tuple->value->int32>=0 && tuple->value->int32<=maximum) *target=tuple->value->int32;
}
#endif
static void inbox(DictionaryIterator *iter,void *context) {
#if defined(PBL_ROUND) && (RALLY_FIXTURE)
 Tuple *round_proof=dict_find(iter,11022);if(round_proof && round_proof->type==TUPLE_INT){r_proof=round_proof->value->int32==1;layer_mark_dirty(s_layer);}
#endif

 (void)context;
 setting(iter,MESSAGE_KEY_Palette,P_PALETTE,6,&s.palette);
 setting(iter,MESSAGE_KEY_Background,P_BG,0xFFFFFF,&s.bg);
 setting(iter,MESSAGE_KEY_Foreground,P_FG,0xFFFFFF,&s.fg);
 setting(iter,MESSAGE_KEY_Accent,P_ACCENT,0xFFFFFF,&s.accent);
 setting(iter,MESSAGE_KEY_TimeFormat,P_TIME,2,&s.time_format);
 setting(iter,MESSAGE_KEY_DateFormat,P_DATE,4,&s.date_format);
#if RALLY_FIXTURE
 fixture_value(iter,11000,23,&f_hour);fixture_value(iter,11001,59,&f_minute);
 fixture_value(iter,11002,59,&f_second);fixture_value(iter,11004,100,&f_battery);s_battery=f_battery;
#endif
 time_t now=time(NULL);tick(localtime(&now),MINUTE_UNIT);
}
static void restore(int key,int maximum,int *target) {
 if(persist_exists(key)) {int value=persist_read_int(key);if(value>=0 && value<=maximum) *target=value;}
}
static void init(void) {
 restore(P_PALETTE,6,&s.palette);restore(P_BG,0xFFFFFF,&s.bg);restore(P_FG,0xFFFFFF,&s.fg);
 restore(P_ACCENT,0xFFFFFF,&s.accent);restore(P_TIME,2,&s.time_format);restore(P_DATE,4,&s.date_format);
 s_window=window_create();s_layer=layer_create(PBL_IF_ROUND_ELSE(GRect(0,0,PBL_DISPLAY_WIDTH,PBL_DISPLAY_HEIGHT),GRect(0,0,200,228)));
 layer_set_update_proc(s_layer,draw);layer_add_child(window_get_root_layer(s_window),s_layer);
 window_stack_push(s_window,true);
 time_t now=time(NULL);tick(localtime(&now),MINUTE_UNIT);battery_changed(battery_state_service_peek());
 tick_timer_service_subscribe(MINUTE_UNIT,tick);battery_state_service_subscribe(battery_changed);
 app_message_register_inbox_received(inbox);app_message_open(256,64);
}
static void deinit(void) {
 tick_timer_service_unsubscribe();battery_state_service_unsubscribe();app_message_deregister_callbacks();
 layer_destroy(s_layer);window_destroy(s_window);
}
int main(void) {init();app_event_loop();deinit();}
