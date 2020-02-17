import os
import pickle
import dill
import importlib


# confirm the directory or create it
def confirm_dir(path):
    if not(os.path.exists(path)):
        os.makedirs(path)
    return path


def create_symlink_of_all_files(src_dir, new_dir):
    """
    Creates a symlink of all files in src_dir to new_dir
    Args:
        src_dir (str): Path to where the files are
        new_dir (str): Path to where the files should be linked

    Returns:
        None
    """
    confirm_dir(new_dir)
    # now go through each file in the model and create and symbolic link to this new directory
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            try:
                os.symlink(os.path.join(root, file), os.path.join(new_dir, file))
            except FileExistsError:
                pass


# pickle save an object
def save_object(save_object, path, name):
    # first confirm the path exits
    confirm_dir(path)
    # make sure the .pickle extension
    full_path = os.path.join(path, __add_pickle(name))
    # now save the object
    with open(full_path, 'wb') as file:
        pickle.dump(save_object, file, 2)


def save_function(saving_function, path, name):
    saving_object = dill.source.importable(saving_function)
    save_object(saving_object, path, name)


# use the dill method to save objects with lambdas (i.e. setattr(.... lambda ...))
def save_object_dill(save_object, path, name):
    # first confirm the path exits
    confirm_dir(path)
    # make sure the .pickle extension
    full_path = os.path.join(path, __add_pickle(name))
    # _object = dill.source.importable(save_object)
    # now save the object
    with open(full_path, 'wb') as file:
        d = dill.dumps(save_object)
        pickle.dump(d, file)
    # exec(_object)
    # with open(full_path + 'o', 'wb') as file:
    #     dill.dump(_object, file)


def __add_pickle(name):
    parts = assert_extension(name)
    if len(parts) == 1:
        return name + '.pickle'

    else:
        return parts[0] + '.pickle'


# check for a pickle extension
def __check_pickle(name):
    parts = assert_extension(name)
    assert parts[1] == 'pickle', 'The file you are trying to import is not a pickle.  Check you have the right path.'


def assert_extension(file_name):
    parts = file_name.split('.')
    assert len(parts) < 3, 'The file name {0} as more than one period'.format(name)
    return parts


# load a pickle object
def load_object(path, name=None):
    # if a name is given then join with the path
    if name is not None:
        name = __add_pickle(name)
        path = os.path.join(path, name)

    # if the object trying to load does not exits return None
    assert os.path.exists(path), 'Looking for pickle object {} but does not exit'.format(path)
        # return None

    # now load the pickle object
    with open(path, 'rb') as file:
        try:
            return pickle.load(file)
        except UnicodeDecodeError:
            return pickle.load(file, encoding='bytes')
        # try:
        #     pass
        # # if there was a key error try decoding from python2
        # except KeyError:
        #     # dill._dill._reverse_typemap["ObjectType"] = object
        #     return pickle.loads(file, encoding='bytes')


def load_function(path, name=None):
    loaded_object = load_object(path, name=name)
    exec(loaded_object)


def serialize_module_type(module):
    return module.__module__


def unserialize_module_type(module):
    name = module.rsplit('.')[-1]
    return getattr(importlib.import_module(name=module), name)


def serialize_lambda(save_object):
    return dill.dumps(save_object)


def un_serialize_lambda(lambda_func):
    return dill.loads(lambda_func)


# load a dill pickle object (see save_object_dill)
def load_object_dill(path, name=None):
    # if a name is given then join with the path
    if name is not None:
        name = __add_pickle(name)
        path = os.path.join(path, name)

    # if the object trying to load does not exits return None
    if not os.path.exists(path):
        return None

    # now load the pickle object
    with open(path, 'rb') as file:
        # try:
        a = pickle.load(file, encoding='latin1')
        b = dill.loads(a)
        return a
        # try loading using the latin1 encoding for python2 objects
        # except UnicodeDecodeError:
        #     return pickle.load(file, encoding = 'latin1')


def join_states(this_state, inherited_state):
    """
    This will join states for the __getstate__ function in pickling objects with parent classes
    Args:
        this_state (tuple): The state to be added to inherited_state
        inherited_state (tuple): The state inherited from parent class

    Returns: tuple of joined state
    """
    return this_state + inherited_state


def separate_states(state, num_of_items):
    """
    This will separate states for the __setstate__ function in pickling objects with parents and children
    Args:
        state (tuple): Current state
        num_of_items (int): Number of items to be taken off

    Returns:
        tuple of tuples for the state of this object and the rest of the inherited state

    """
    inherited_state = state[num_of_items:]
    state = state[:num_of_items]
    return state, inherited_state

