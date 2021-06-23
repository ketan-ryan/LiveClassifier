from mega import Mega
import datetime
import logging


class InsufficientStorageError(Exception):
    pass


# Handles interaction with the MEGA cloud
class MegaHandler:
    # Buffer = max no of items to be deleted in one pass
    def __init__(self, buffer=7):
        mega = Mega()
        with open('secrets.txt', 'r') as fp:
            email = fp.readline().strip()
            pw = fp.readline().strip()
            self.m = mega.login(email, pw)
        self.logger = logging.getLogger(__name__)
        self.buffer = buffer

    # Uploads a video to the cloud, organized by time and location
    def put_video(self, video, location, day):
        if self.check_space():
            year = datetime.datetime.year
            root = f'{year}'
            if self.m.find(root) is None:
                self.m.create_folder(root)
            loc = f'{root}/{location}'
            if self.m.find(loc) is None:
                self.m.create_folder(loc)
            day = f'{location}/{day}'
            if self.m.find(day) is None:
                self.m.create_folder(day)
            folder = self.m.find(day)
            self.m.upload(video, folder[0])
            return self.m.export(f'{folder}/{video}')
        else:
            raise InsufficientStorageError()

    # Ensures there is enough cloud storage to upload a video. If there is less than 1GB, items are deleted either
    # up to the buffer or until there is greater than 1GB.
    def check_space(self):
        quota = (self.m.get_quota()) / 1000
        space = self.m.get_storage_space(giga=True)
        cap = space - quota
        if 2 >= cap > 1:
            self.logger.warning('Disk space low! Items will soon be deleted, please make sure to download any files'
                                'you wish to keep.')
        elif cap <= 1:
            self.logger.warning('Disk space very low! Items will now begin being destroyed to reclaim space.')
            files = self.m.get_files()

            buff = 0
            for file in files[::-1]:
                self.logger.info(f'Permanently deleting file {file} ...')
                self.m.destroy(file[0])
                buff += 1
                cap = space - quota
                if 2 >= cap > 1:
                    self.logger.info(f'{buff} files have been deleted. You now have {cap} GB of storage remaining. '
                                     f'Please review your files and save any you wish to keep.')
                    return False
                elif buff >= self.buffer:
                    self.logger.info(f'{buff} files have been deleted. You have reached your threshold of {self.buffer}'
                                     f' deleted files per pass. You only have {cap} GB of storage remaining. Please '
                                     f'review your files and save any you wish to keep.')
                    return False
        return True
