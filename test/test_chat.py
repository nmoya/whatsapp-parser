import os

class TestChat:
    def test_chat(self, tmpdir):
        out_filename = str(tmpdir.join("abc"))
        for case in ['One', 'Two']:
            cmd = 'python wp_parser/wp_chat.py -f test/testChat2.txt -n Username{} > {}'.format(case, out_filename)
            os.system(cmd)
            with open(out_filename) as fh:
                result = fh.read()
            expected_file = 'test/out/testChat2_Username{}.out'.format(case)
            with open(expected_file) as fh:
                expected = fh.read()
            assert result == expected
