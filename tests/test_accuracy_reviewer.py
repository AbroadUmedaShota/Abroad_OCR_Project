import json
import os
import subprocess
import tempfile
import unittest

from scripts.accuracy_reviewer import load_ground_truth, load_ocr_results


class TestAccuracyReviewer(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.temp_path = self.tempdir.name

    def tearDown(self):
        self.tempdir.cleanup()

    def _write_csv(self, name: str, header: str, rows: str) -> str:
        path = os.path.join(self.temp_path, name)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(header)
            if not header.endswith('\n'):
                f.write('\n')
            f.write(rows)
            if not rows.endswith('\n'):
                f.write('\n')
        return path

    def _write_json(self, name: str, data) -> str:
        path = os.path.join(self.temp_path, name)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        return path

    def test_load_ocr_results_missing_file(self):
        missing_path = os.path.join(self.temp_path, 'missing.csv')
        with self.assertRaisesRegex(RuntimeError, 'ファイルが見つかりません'):
            load_ocr_results(missing_path)

    def test_load_ocr_results_invalid_values(self):
        csv_path = self._write_csv(
            'invalid.csv',
            'page,block_id,x0,y0,x1,y1,text,confidence',
            'A,0,0,0,10,10,テスト,high'
        )
        with self.assertRaisesRegex(RuntimeError, '数値が不正'):
            load_ocr_results(csv_path)

    def test_load_ground_truth_invalid_json(self):
        json_path = os.path.join(self.temp_path, 'invalid.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write('{ invalid json')
        with self.assertRaisesRegex(RuntimeError, '形式が不正'):
            load_ground_truth(json_path)

    def test_script_propagates_runtime_error(self):
        gt_path = self._write_json('gt.json', {"1": []})
        env = os.environ.copy()
        env['PYTHONPATH'] = os.getcwd() + os.pathsep + env.get('PYTHONPATH', '')

        result = subprocess.run(
            [
                'python',
                'scripts/accuracy_reviewer.py',
                '--ocr_csv', os.path.join(self.temp_path, 'does_not_exist.csv'),
                '--ground_truth_json', gt_path,
            ],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            env=env,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('OCR結果CSVファイルが見つかりません', result.stderr)


if __name__ == '__main__':
    unittest.main()
