# Desktop file
desktop_file = configure_file(
  input: 'dss-installer.desktop.in',
  output: 'dss-installer.desktop',
  copy: true,
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

subdir('icons')
