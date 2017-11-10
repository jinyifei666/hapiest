from enum import Enum
from hapi import *
from threading import Thread
from hapiest_util import *
from worker import *

# An enum for all possible errors that could be encountered while verifying fetch parameters
# and while actually fetching the data
class FetchErrorKind(Enum):
    BadParameter = 1            # This wont be used
    BadParameterGroup = 2       # This wont be used
    BadNuMin = 3                # This wont be used
    BadNuMax = 4                # This wont be used
    BadConnection = 5
    BadIsoList = 6
    FailedToRetreiveData = 7
    FailedToOpenThread = 8
    EmptyName = 9

# A class that contains a FetchErrorKind along with a description for the error
class FetchError(object):

    # Constructor for FetchError
    #
    # errors: a FetchErrorKind object
    # description: a textual description of the error
    def __init__(self, error, description = ''):
        self.error = error
        self.description = description

class DataHandle(object):
    DATA_FILE_REGEX = re.compile('(?P<data_handle>.+)\\.data\\Z')

    # Returns a list of all the different data-names in the data directory
    @staticmethod
    def get_all_data_names():
        files = listdir(Config.data_folder)
        datas = []
        for f in files:
            match = DataHandle.DATA_FILE_REGEX.match(f)
            if match == None:
                continue
            datas.append(match.groupdict()['data_handle'])
        return datas

    def __init__(self, data_name):
        self.data_name = data_name


    # A safer handle to the try_fetch function that provides feedback on parameters
    # if they're invalid.
    #
    # RETURNS:
    # True if the fetch went through successfully
    #
    # iso_id_list:      the list of all of the global id's of the isotopologues
    #                   that data should be fetched on.
    # numin:            minimum wavenumber
    # numax:            maximum wavenumber
    # parameter_groups: any aditional groups of parameters to include in the fetch
    # parameters        any additional individual parameters to include in the fetch
    def try_fetch(self, fetch_window, iso_id_list, numin, numax, parameter_groups = [], parameters = []):
        fetch_window.disable_fetch_button()
        work = HapiWorker.echo(
            data_name=self.data_name,
            iso_id_list=iso_id_list,
            numin=numin,
            numax=numax,
            parameter_groups=parameter_groups,
            parameters=parameters)
        work['type'] = Work.FETCH
        self.worker = HapiWorker(work, callback=lambda x: fetch_window.fetch_done(x))
        self.worker.start()
        return self.worker
