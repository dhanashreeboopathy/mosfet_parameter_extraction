module mosfet_parameter_extraction( input reset,
                 input A, 
                 output Z );
//reset does nothing
assign Z= !A;

endmodule
