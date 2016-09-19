import os
import re


if __name__ == '__main__':
    print("Preparing run list")

    dst_loc = os.environ['S3_DST_PATH']
    src_loc = os.environ['S3_SRC_PATH']
    test_pfx = ''

    if 'Test-' in os.environ['GO_PIPELINE_NAME']:
        test_pfx = "test/"


    p_src = re.compile(src_loc + "([^_]+)_([^_]+)_.+")
    p_dst = re.compile(test_pfx + dst_loc + "([^_]+)_([^_]+)_.+")

    dst = {}

    run_list = open("run-list.txt",'w')

    # Read Src List
    with open('dst-list/dst-list.txt', 'r') as src_list:
        for l in src_list:
            l = l.rstrip().lstrip()

            m = p_dst.match(l)

            if m is None:
                raise RuntimeError("Cannot parse [{}]".format(l))

            key = m.group(1) + "_" + m.group(2)
            dst[key] = l

    with open('src-list/src-list.txt') as dst_list:
        for l in dst_list:
            l = l.rstrip().lstrip()

            m = p_src.match(l)

            if m is None:
                raise RuntimeError("Cannot parse [{}]".format(l))

            key = m.group(1) + "_" + m.group(2)

            if key not in dst:
                    run_list.write(l + '\n')

