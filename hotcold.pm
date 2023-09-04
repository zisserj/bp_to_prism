dtmc

formula is_cold_requested = (is_cold_bt_requesting_cold=true) | (is_hot_bt_requesting_cold=true) | (is_interleave_bt_requesting_cold=true);
formula is_hot_requested = (is_hot_bt_requesting_hot=true) | (is_cold_bt_requesting_hot=true) | (is_interleave_bt_requesting_hot=true);
formula is_x_requested = (is_cold_bt_requesting_x=true) | (is_hot_bt_requesting_x=true) | (is_interleave_bt_requesting_x=true); 

formula is_cold_blocked = (is_cold_bt_blocking_cold=true) | (is_hot_bt_blocking_cold=true) | (is_interleave_bt_blocking_cold=true);
formula is_hot_blocked = (is_hot_bt_blocking_hot=true) | (is_cold_bt_blocking_hot=true) | (is_interleave_bt_blocking_hot=true);
formula is_x_blocked = (is_cold_bt_blocking_x=true) | (is_hot_bt_blocking_x=true) | (is_interleave_bt_blocking_x=true);

formula is_cold_selected = (is_cold_requested=true) & (is_cold_blocked=false);
formula is_hot_selected = (is_hot_requested=true) & (is_hot_blocked=false);
formula is_x_selected = (is_x_requested=true) & (is_x_blocked=false);

label "hot" = (is_hot_selected=true);
label "cold" = (is_cold_selected=true);
label "x" = (is_x_selected=true);


/////////////////////////////////////////////////////////
formula is_hot_bt_requesting_hot = (s_hot=0) | (s_hot=1);
formula is_hot_bt_requesting_cold = false;
formula is_hot_bt_requesting_x = false;

formula is_hot_bt_blocking_hot = false;
formula is_hot_bt_blocking_cold = false;
formula is_hot_bt_blocking_x = false;
module hot_bt
	s_hot : [0..2] init 0;
    [XX] s_hot=0 & (is_x_selected=true)-> 1: (s_hot'=0);
    [COLD] s_hot=0 & (is_cold_selected=true)-> 1: (s_hot'=0);
	[HOT] (s_hot=0) & (is_hot_selected=true) -> 1 : (s_hot'=1) ;


    [XX] s_hot=1 & (is_x_selected=true)-> 1: (s_hot'=1);
    [COLD] s_hot=1 & (is_cold_selected=true)-> 1: (s_hot'=1);
	[HOT] (s_hot=1) & (is_hot_selected=true) -> 1 : (s_hot'=2) ;

	[XX] (s_hot=2) -> 1 : (s_hot'=2);
	[HOT] (s_hot=2) -> 1 : (s_hot'=2);
	[COLD] (s_hot=2) -> 1 : (s_hot'=2);
endmodule

/////////////////////////////////////////////////////////
formula is_cold_bt_requesting_cold = (s_cold=0) | (s_cold=1);
formula is_cold_bt_requesting_hot = false;
formula is_cold_bt_requesting_x = false;

formula is_cold_bt_blocking_cold = false;
formula is_cold_bt_blocking_hot = false;
formula is_cold_bt_blocking_x = false;
module cold_bt
	s_cold : [0..2] init 0;
	
    [XX] s_cold=0 & (is_x_selected=true)-> 1: (s_cold'=0);
    [HOT] s_cold=0 & (is_hot_selected=true)-> 1: (s_cold'=0);
	[COLD] (s_cold=0) & (is_cold_selected=true) -> 1 : (s_cold'=1);
    
    [XX] s_cold=1 & (is_x_selected=true)-> 1: (s_cold'=1);
    [HOT] s_cold=1 & (is_hot_selected=true)-> 1: (s_cold'=1);
	[COLD] (s_cold=1) & (is_cold_selected=true) -> 1 : (s_cold'=2);

	[XX] (s_cold=2) -> 1 : (s_cold'=2);
	[HOT] (s_cold=2) -> 1 : (s_cold'=2);
    [COLD] (s_cold=2) -> 1 : (s_cold'=2);
endmodule

////////////////////////////////////////////////////////
formula is_interleave_bt_requesting_cold = false;
formula is_interleave_bt_requesting_hot = false;
formula is_interleave_bt_requesting_x = (s_interleave=0) | (s_interleave=1);

formula is_interleave_bt_blocking_cold = s_interleave=0;
formula is_interleave_bt_blocking_hot = s_interleave=1;
formula is_interleave_bt_blocking_x = false;

module interleave_bt
	s_interleave: [0..1] init 0;

	[XX] (s_interleave=0) & (is_x_selected=true)  -> 1 : (s_interleave'=0);
	[COLD] (s_interleave=0) & (is_cold_selected=true)  -> 1 : (s_interleave'=0);
	[HOT] (s_interleave=0) & (is_hot_selected=true)  -> 1 : (s_interleave'=1);

	[XX] (s_interleave=1) & (is_x_selected=true)  -> 1 : (s_interleave'=1);
	[HOT] (s_interleave=1) & (is_hot_selected=false)  -> 1 : (s_interleave'=1);
	[COLD] (s_interleave=1) & (is_cold_selected=true) -> 1 : (s_interleave'=0);
endmodule

