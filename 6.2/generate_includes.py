import os;

index = 1
for root, dirs, files in os.walk("include"):
	sub_root = root[8:]
	if files :
		print ("nested" + str(index) + "Include: { #destination = ${d_include}"+ sub_root +"; \"" + root+ "\*\"};")
		index += 1
		