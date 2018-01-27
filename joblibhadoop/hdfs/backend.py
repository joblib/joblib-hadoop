"""Joblib storage backend for HDFS."""

import datetime
import re
import os.path
import hdfs3
from joblib._store_backends import (StoreBackendBase, StoreBackendMixin,
                                    CacheItemInfo)

DEFAULT_BACKEND_OPTIONS = dict(host='localhost', port=9000, user=None,
                               ticket_cache=None, token=None, pars=None,
                               connect=True)


class HDFSStoreBackend(StoreBackendBase, StoreBackendMixin):
    """A StoreBackend for Hadoop storage file system (HDFS)."""

    def _open_item(self, f, mode):
        return self.storage.open(f, mode)

    def _item_exists(self, path):
        return self.storage.exists(path)

    def _move_item(self, src, dst):
        return self.storage.mv(src, dst)

    def clear_location(self, location):
        """Check if object exists in store."""
        self.storage.rm(location, recursive=True)

    def create_location(self, location):
        """Create object location on store."""
        self._mkdirp(location)

    def get_items(self):
        """Return the whole list of items available in cache."""
        cache_items = []
        try:
            self.storage.ls(self.location)
        except IOError:
            return []

        for path in self.storage.walk(self.location):
            is_cache_hash_dir = re.match('[a-f0-9]{32}$',
                                         os.path.basename(path))

            if is_cache_hash_dir:
                output_filename = os.path.join(path, 'output.pkl')
                try:
                    last_access = self.storage.info(
                        output_filename)['last_access']
                except IOError:  # pragma: no cover
                    try:
                        last_access = self.storage.info(path)['last_access']
                    except IOError:
                        # The directory has already been deleted
                        continue
                dirsize = self.storage.info(output_filename)['size']

                last_access = datetime.datetime.fromtimestamp(last_access)
                cache_items.append(CacheItemInfo(path, dirsize, last_access))

        return cache_items

    def _check_options(self, options):
        for k, v in DEFAULT_BACKEND_OPTIONS.items():
            if k not in options:
                options[k] = v

        return options

    def configure(self, location, verbose=0,
                  backend_options=DEFAULT_BACKEND_OPTIONS):
        """Configure the store backend."""

        options = self._check_options(backend_options.copy())
        self.storage = hdfs3.HDFileSystem(
            host=options['host'], port=options['port'], user=options['user'],
            ticket_cache=options['ticket_cache'], token=options['token'],
            pars=options['pars'], connect=options['connect'])
        if location.startswith('/'):
            location = location[1:]
        self.location = location
        self.storage.mkdir(self.location)

        # computation results can be stored compressed for faster I/O
        self.compress = options['compress']

        # Memory map mode is not supported
        self.mmap_mode = None

    def _mkdirp(self, directory):
        """Create recursively a directory on the HDFS file system."""
        current_path = ""
        for sub_dir in directory.split('/'):
            current_path = os.path.join(current_path, sub_dir)
            self.storage.mkdir(current_path)
