import unittest
import os
import subprocess
import glob

class TestOcrPoc(unittest.TestCase):

    def setUp(self):
        """Set up test variables."""
        self.test_pdf_path = os.path.abspath("tests/test.pdf")
        self.base_name = os.path.splitext(os.path.basename(self.test_pdf_path))[0]
        self.pdf_dir = os.path.dirname(self.test_pdf_path)
        
        self.output_pdf_path = os.path.join(self.pdf_dir, f"{self.base_name}_searchable.pdf")
        self.output_csv_path = os.path.join(self.pdf_dir, f"{self.base_name}_ocr_results.csv")
        self.output_zip_path = os.path.join(self.pdf_dir, f"{self.base_name}.zip")
        self.temp_images_folder = "temp_images"

    def tearDown(self):
        """Clean up generated files."""
        files_to_remove = [
            self.output_pdf_path,
            self.output_csv_path,
            self.output_zip_path,
        ]
        for f in files_to_remove:
            if os.path.exists(f):
                os.remove(f)
        
        # Clean up intermediate images
        if os.path.exists(self.temp_images_folder):
            for img_file in glob.glob(os.path.join(self.temp_images_folder, "*.png")):
                os.remove(img_file)
            os.rmdir(self.temp_images_folder)
            
        # Clean up debug files
        for debug_file in glob.glob("debug_ocr_result_page_*.txt"):
            os.remove(debug_file)

    def test_cli_execution_and_output_generation(self):
        """
        Tests the full CLI execution of ocr_poc.py with PDF, CSV, and ZIP output.
        """
        # Ensure the input test PDF exists
        self.assertTrue(os.path.exists(self.test_pdf_path), f"Test PDF not found at {self.test_pdf_path}")

        # Run the script as a subprocess
        command = [
            "python", 
            os.path.abspath("src/ocr_poc.py"), 
            self.test_pdf_path,
            "--zip"
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        # Print stdout/stderr for debugging if the test fails
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

        # Assert that all expected files were created
        self.assertTrue(os.path.exists(self.output_pdf_path), f"Searchable PDF was not created at {self.output_pdf_path}")
        self.assertTrue(os.path.exists(self.output_csv_path), f"OCR results CSV was not created at {self.output_csv_path}")
        self.assertTrue(os.path.exists(self.output_zip_path), f"ZIP archive was not created at {self.output_zip_path}")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)