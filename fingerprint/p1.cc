// Ardi Artani
// Group Project

// p1 {input gray–level image} {input gray–level threshold} {output binary image}.
// Select any threshold that results in ”clean” binary images from the gray–level ones given
// to you (a binary image can be saved as a PGM file with 1 as the number of colors in the
// header). You should be able to use the same threshold value for all images. Please, when
// you submit your assignment, indicate the value you used in your README file. Apply
// program p1 to the image two objects.pgm. (3 points)

// compile: make ./p1
// run: ./p1 input_image.pgm 125 output_image.pgm

#include "image.h"
#include <iostream>
#include <string>
#include <cstdio>

using namespace std;
using namespace ComputerVisionProjects;

int main(int argc, char **argv){

	// for p1 we accept 3 args; input file, threshold and the output file
	if (argc != 4) {
		printf("Usage: %s input_image.pgm 125 out_binary_image.pgm\n", argv[0]);
		return 0;
	}
	
	const string input_file(argv[1]);
	// convert threshold var string to an integer
	const int threshold_ = stoi(argv[2]); 
	const string output_file(argv[3]);

	Image an_image;
	
	if (!ReadImage(input_file, &an_image)) {
		cout <<"Can't open file " << input_file << endl;
		return 0;
	}

	// for loop through the input image and set pixel to 0 or 255 depending on our threshold given
	for (unsigned int i = 0; i < an_image.num_rows(); i++)
	{
		for (unsigned int j = 0; j < an_image.num_columns(); j++) 
		{
			// if image pixel is less than our threshold_ set image pixel to 0 otherwise to 255
			an_image.GetPixel(i, j) <= threshold_ ? an_image.SetPixel(i, j, 0) : an_image.SetPixel(i, j, 255);
		}
	}
	
	if (!WriteImage(output_file, an_image)){
		cout << "Can't write to file " << output_file << endl;
		return 0;
	} else {
		cout << "Program 1 successfully executed at threshold "<< threshold_ << " and output filename " << output_file << endl;
	}
}