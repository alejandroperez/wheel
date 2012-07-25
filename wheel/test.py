import os
import pkg_resources

from nose.tools import assert_true, assert_false, assert_equal, raises
from .install import WheelFile


def test_findable():
    """Make sure pkg_resources can find us."""
    assert pkg_resources.working_set.by_key['wheel'].version


def test_egg_re():
    """Make sure egg_info_re matches."""
    from . import egg2wheel
    import pkg_resources
    egg_names = open(pkg_resources.resource_filename('wheel', 'eggnames.txt'))
    for line in egg_names:
        line = line.strip()
        if not line: continue
        assert egg2wheel.egg_info_re.match(line), line


def test_compatibility_tags():
    wf = WheelFile("package-1.0.0-cp32.cp33-noabi-noarch.whl")
    assert_equal(list(wf.compatibility_tags),
                 [('cp32', 'noabi', 'noarch'), ('cp33', 'noabi', 'noarch')])
    assert_equal(wf.arity, 2)
    
    wf2 = WheelFile("package-1.0.0-1st-cp33-noabi-noarch.whl")
    wf2_info = wf2.parsed_filename.groupdict()
    assert wf2_info['build'] == '1st', wf2_info


def test_bdist_wheel():
    import distutils
    os.chdir(pkg_resources.working_set.by_key['wheel'].location)
    distutils.core.run_setup("setup.py", ["bdist_wheel"])


def test_util():
    import wheel.util
    for i in range(10):
        before = b'*' * i
        encoded = wheel.util.urlsafe_b64encode(before)
        assert not encoded.endswith(b'=')
        after = wheel.util.urlsafe_b64decode(encoded)
        assert before == after


def test_pick_best():
    def get_tags(res):
        info = res[-1].parsed_filename.groupdict()
        return info['pyver'], info['abi'], info['plat']

    from wheel.install import pick_best, WheelFile
    
    cand_tags = [('py27', 'noabi', 'noarch'), ('py26', 'noabi', 'noarch'),
                 ('cp27', 'noabi', 'linux_i686'), ('cp26', 'noabi', 'linux_i686'),
                 ('cp27', 'noabi', 'linux_x86_64'), ('cp26', 'noabi', 'linux_x86_64')]
    cand_wheels = [WheelFile('testpkg-1.0-%s-%s-%s.whl' % t) for t in cand_tags]

    supported = [('cp27', 'noabi', 'linux_i686'), ('py27', 'noabi', 'noarch')]
    supported2 = [('cp27', 'noabi', 'linux_i686'), ('py27', 'noabi', 'noarch'),
                  ('cp26', 'noabi', 'linux_i686'), ('py26', 'noabi', 'noarch')]
    supported3 = [('cp26', 'noabi', 'linux_i686'), ('py26', 'noabi', 'noarch'),
                  ('cp27', 'noabi', 'linux_i686'), ('py27', 'noabi', 'noarch')]

    for supp in (supported, supported2, supported3):
        assert_equal(get_tags(pick_best(cand_wheels, supp)), supp[0])
        assert_equal(map(get_tags, pick_best(cand_wheels, supp, top=False)), supp)


if __name__ == '__main__':
    import nose
    nose.main()
