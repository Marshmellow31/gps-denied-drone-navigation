import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import final_dataset_analysis_geometry_v2_compat as compat


class AnalysisCompatibilityTests(unittest.TestCase):
    def test_primary_identity_removes_only_shared_secondary_metadata(self):
        nested={'reviewed_artifact_hashes':{'original':'locked'}}
        expected={'backend':'FAST-LIO','runtime':nested,'unknown':'must-remain',compat.KEY:123.0}
        result=compat.primary_identity(expected,{compat.KEY:123.0})
        self.assertEqual(result,{'backend':'FAST-LIO','runtime':nested,'unknown':'must-remain'})
        self.assertIn(compat.KEY,expected)
        self.assertIs(result['runtime'],nested)

    def test_missing_or_changed_threshold_metadata_is_rejected(self):
        for expected,gate in (({},{}),({compat.KEY:123.0},{}),({compat.KEY:123.0},{compat.KEY:124.0})):
            with self.subTest(expected=expected,gate=gate),self.assertRaises(ValueError):
                compat.primary_identity(expected,gate)

    def test_review_rejection_precedes_result_analysis(self):
        with tempfile.TemporaryDirectory() as folder:
            review=Path(folder)/'review.md';review.write_text('**Gate:** REVISE\n')
            with patch.object(compat.original,'analyze',side_effect=AssertionError('results were opened')) as forbidden:
                with self.assertRaisesRegex(ValueError,'has not passed'):
                    compat.analyze(Path('/unopened'),Path('/unopened'),Path('/unopened'),Path('/unopened'),Path('/unopened'),review,Path(folder)/'result.json')
                forbidden.assert_not_called()

    def test_adapter_delegates_original_checks_and_restores_loader(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'result.json'
            def original_loader(*args):
                self.assertEqual(args[-1],{'native':'primary'})
                self.assertEqual(args[-2],{compat.KEY:123.0})
                return 'original checks retained'
            def original_analysis(*args):
                self.assertEqual(compat.original.load_scene(None,None,14,'fixture','CORRIDOR',{compat.KEY:123.0},{'native':'primary',compat.KEY:123.0}), 'original checks retained')
                return {'status':'analytic fixture'}
            with patch.object(compat,'require_compatibility_review',return_value={'accepted':'fixture'}), patch.object(compat.original.workflow,'require_r3_pass'), patch.object(compat.original,'load_scene',original_loader), patch.object(compat.original,'analyze',original_analysis):
                result=compat.analyze(None,None,None,None,None,None,output)
                self.assertIs(compat.original.load_scene,original_loader)
                self.assertEqual(result['status'],'analytic fixture')
                self.assertTrue(output.exists())

    def test_original_failure_is_propagated_and_loader_restored(self):
        saved=compat.original.load_scene
        with patch.object(compat,'require_compatibility_review',return_value={}), patch.object(compat.original.workflow,'require_r3_pass'), patch.object(compat.original,'analyze',side_effect=ValueError('output identity changed')):
            with self.assertRaisesRegex(ValueError,'output identity changed'):
                compat.analyze(None,None,None,None,None,None,None)
            self.assertIs(compat.original.load_scene,saved)


if __name__ == '__main__':unittest.main()
