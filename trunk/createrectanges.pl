#!/usr/bin/perl -w
use strict;

die "Syntax: 'number of rectanges horizontally' 'number of rectanges vertically' 'skip rectangles in x-y,x-y eg: 0-1;2-3' 'unite rectangles in row at position eg: 1,2-3;2,1-3'" unless scalar(@ARGV)>=2;

my $width = $ARGV[0];
my $height = $ARGV[1];
my @skip = exists $ARGV[2] ? split(/;/, $ARGV[2]) : ();
my @unite = exists $ARGV[3] ? split(/;/, $ARGV[3]) : ();
my @horizontal_labels = exists $ARGV[4] ? split(/;/, $ARGV[4]) : ();
my @vertical_labels = exists $ARGV[5] ? split(/;/, $ARGV[5]) : ();

my $svg_header = '<?xml version="1.0" standalone="no"?>'."\n";
$svg_header .= '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"'."\n";
$svg_header .= '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'."\n";
$svg_header .= '<svg xmlns="http://www.w3.org/2000/svg" version="1.1">'."\n";
my $svg_tail = '</svg>';
my $svg_body = '';
my $text_space_x = 90;
my $text_space_y = 25;

for(my $i=0; $i<$width; $i++) {
	my $x = $text_space_x + 25 * $i;
	$svg_body .= '<text x="'.($x+2).'" y="15" fill="black" >'.$horizontal_labels[$i]."</text>\n" if exists $horizontal_labels[$i] and $horizontal_labels[$i] ne "-" ;
}

for(my $j=0; $j<$height; $j++) {
	my $y = $text_space_y + 25 * $j;
	$svg_body .= '<text x="10" y="'.($y+15).'" fill="black">'.$vertical_labels[$j].'</text>' if exists $vertical_labels[$j] and $vertical_labels[$j] ne "-";
    for(my $i=0; $i<$width; $i++) {
		my $x = $text_space_x + 25 * $i;
		
	
		# draw_range function checks whether it has to draw a large rectangle at the given position and return how many of next rectange positions has been occupied:
		my $range_length = draw_range($i, $j);
		if($range_length) {
			$i+=$range_length;
			next;
		}
		$svg_body .= '<rect '.get_title($i,$j).'x="'.$x.'" y="'.$y.'" width="20" height="20" fill="#cccccc" style="stroke:black;stroke-width:2" />'."\n" unless skip_rectangle($i,$j);	
    }
}

print "$svg_header\n$svg_body$svg_tail\n";

sub get_title {
	my $i = shift;
    my $j = shift;
	my $title = "";	
	if (exists $horizontal_labels[$i] and $horizontal_labels[$i] ne "-" and exists $vertical_labels[$j] and $vertical_labels[$j] ne "-") {
		$title = 'title="'.$vertical_labels[$j].'-'.$horizontal_labels[$i].'" '; 
	}
	return $title;
}

sub draw_range {
    my $i = shift;
    my $j = shift;
    foreach my $e (@unite) {
        my ($a, $range) = split(/,/, $e);
        if($a==$j) {
	    my ($r1,$r2) = split(/\-/, $range);
	    if($r1 == $i) {
		my $width = 20 + 25*($r2-$r1);
		my $x = $text_space_x + 25 * $i;
	    my $y = $text_space_y + 25 * $j;
		$svg_body .= '<rect '.get_title($i,$j).'x="'.$x.'" y="'.$y.'" width="'.$width.'" height="20" fill="#cccccc" style="stroke:black;stroke-width:2" />'."\n";
		return $r2-$r1;
	    }
	}
    }
    return 0;
}

sub skip_rectangle {
    my $x = shift;
    my $y = shift;
    foreach my $e (@skip) {
        my ($a,$b) = split(/\-/, $e);
	return 1 if $a == $x and $b == $y;
    }
    return 0;
}