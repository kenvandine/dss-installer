moduledir = join_paths(pkgdatadir, 'dss_installer')
gnome = import('gnome')

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('pkgdatadir', pkgdatadir)


configure_file(
  input: 'dss-installer.in',
  output: 'dss-installer',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

sources = [
  'banner.png',
  'console.py',
  'main.py',
]

install_data(sources, install_dir: moduledir)

scripts = [
  'bootstrap.sh',
  'initialize.sh',
  'setup.sh',
]
install_data(scripts, install_dir: pkgdatadir, install_mode: 'rwxr-xr-x')
