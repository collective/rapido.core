import unittest
import doctest
from pprint import pprint

optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE

TESTFILES = [
    'rapido.rst',
]


def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(
            filename,
            optionflags=optionflags,
            globs={
              'pprint': pprint,
            }
        ) for filename in TESTFILES
    ])

if __name__ == '__main__':                                 # pragma NO COVERAGE
    unittest.main(defaultTest='test_suite')                # pragma NO COVERAGE
