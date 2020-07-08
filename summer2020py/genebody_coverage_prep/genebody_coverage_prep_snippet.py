    if os.path.exists(output.gbdy_prep):
	print("output directory exists, deleting gbdy_prep:", output.gbdy_prep)
	shutil.rmtree(output.gbdy_prep)

    print("making output directory gbdy_prep:", output.gbdy_prep)
    os.mkdir(output.gbdy_prep)

    for cur_sample in SAMPLES:
	print("cur_sample:", cur_sample)
	cur_dir = os.path.join(output.gbdy_prep, cur_sample)
	os.mkdir(cur_dir)

	cur_search = os.path.join(input.dir, cur_sample + "*")
	print("cur_search:", cur_search)
	cur_file_list = glob.glob(cur_search)
	cur_file_list.sort()
	print("cur_file_list:", cur_file_list)

	for cur_file in cur_file_list:
	    basename = os.path.basename(cur_file)
	    dst = os.path.join(cur_dir, basename)
	    print("dst:", dst)

	    os.symlink(cur_file, dst)

