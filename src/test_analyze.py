import json
import os
import subprocess
from unittest import TestCase


class TestUtil(TestCase):
    TEST_DATA = "../test_data"
    INFILE = "analyze_in.json"
    OUTFILE = "analyze_out.json"

    def test_invoke(self):
        outfile_path = "{test_data_path}/{out_file}".format(test_data_path=self.TEST_DATA, out_file=self.OUTFILE)
        os.system(
            "aws lambda invoke --function-name analyze "
            "--payload file://{test_data_path}/{in_file} outfile_path".format(
                test_data_path=self.TEST_DATA, in_file=self.INFILE, outfile_path=outfile_path,
            )
        )
        with open(outfile_path) as f:
            result = json.load(f)
            assert result["statusCode"] == 200
            response = json.loads(result["response"])
            assert response["total"] == 10.13

        # print(subprocess.check_output([
        #     "aws", "lambda", "invoke",
        #     "--function-name", "analyze"
        #                        "--payload", '{"path": "receipts/DSC_3607.JPG"}',
        #     "analyze_test.txt"
        # ]))
