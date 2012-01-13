import os
import sys
import subprocess
import logging
import zc.buildout

from zest.recipe.mk_buildout.mk_buildout import MakeBuildout

class CreateRunner(object):
    _base_options = {'runner_name': 'test_all'}
    
    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = {}
        self.options.update(self._base_options)
        self.options.update(options)

    @property
    def logger(self):
        return logging.getLogger(self.name)

    def _write_runner(self, f, part_id):
        part = self.buildout[part_id]
        runner = part.get('test_runner', 'bin/test')
        location = os.getcwd()

        f.write('print "********************************************************************************"\n')
        f.write('print "Running tests for buildout %s"\n' % part_id)
        f.write('print "********************************************************************************"\n')

        f.write('os.chdir("%s")\n' % os.sep.join([
            self.buildout['buildout']['parts-directory'],
            part_id]))
        f.write('p = subprocess.Popen(["%s"] + args)\n' % runner)
        f.write('p.wait()\n\n')

    def install(self):
        parts = []
        buildout_parts = self.buildout['buildout']['parts'].split('\n')

        for part_id in self.buildout.keys():
            if not getattr(self.buildout[part_id], 'recipe', None):
                # No recipe, let's skip that.
                continue

            if not part_id in buildout_parts:
                continue

            if isinstance(self.buildout[part_id].recipe, MakeBuildout):
                parts.append(part_id)

        exe = open(os.sep.join(['bin', self.options['runner_name']]),
                   'w')

        exe.write('\n'.join(['#!%s' % sys.executable,
                             'import os',
                             'import subprocess',
                             'import sys'
                             '',
                             'args = sys.argv',
                             '']))


        for part_id in parts:
            self._write_runner(exe, part_id)

        exe.close()
        return []

    def update(self):
        return self.install()
    
