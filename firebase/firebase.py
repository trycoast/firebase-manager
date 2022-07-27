import operator
from functools import reduce
import firebase_admin
from firebase_admin import credentials, db, auth
from pydantic.utils import deep_update


class Firebase:
    """ reads and writes data to the database. """

    def __init__(self, creds: str, url: str, cache: bool = True, name: str = None, rel_path: str = '') -> None:
        """ Initializes the Firebase object.

        Args:
            creds (str): The path to the credentials file.
            url (str): The url of the database.
            cache (bool, optional): Whether or not to cache the data.
            name (str, optional): The name of the database (required if running multiple instances).
            rel_path (str, optional): The relative path inside database to shrink path args and isolate data access.
        """
        db_credentials = credentials.Certificate(creds)
        firebase_admin.initialize_app(db_credentials, {'databaseURL': url}, name=name if name else '[DEFAULT]')
        self.auth = auth

        if rel_path:
            rel_path = rel_path + '/' if rel_path[-1] != '/' else rel_path
        self.rel_path = rel_path

        if cache:
            self.ref = db.reference(f'{self.rel_path}' if rel_path else "/").get()
            self.ref = self.ref if self.ref else {}  # if the database is empty, the reference will be None.
        else:
            self.ref = {}

        self.rel_path = rel_path
        self.ref = db.reference(f'{rel_path}' if rel_path else "/").get() if cache else None   # NOTE: might become problematic once database reaches a certain size.
        self.ref = self.ref if self.ref or cache is False else {}

    def __call__(self, path: str, shallow: bool = False) -> dict:
        """ Returns the data at the specified path.

        Args:
            path (str): The path to the data.
            shallow (bool, optional): Whether or not to return a shallow copy of the data.

        Returns:
            dict: The data at the specified path.
        """
        # print(self.rel_path + path, 'this is the call')
        if self.ref is not None:
            return self.obtain(self.ref, self.make_keys(path))
        data = db.reference(self.rel_path + path).get(shallow=shallow)
        return data if data else {}

    @staticmethod
    def validate(data: dict) -> None:
        """ Validates the data.

        Args:
            data (dict): The data to validate.

        Raises:
            TypeError: If the data is not a dict.
            ValueError: If the dict keys contain forbidden characters.
        """
        ok_type = isinstance(data, dict)
        if not ok_type:
            raise TypeError(f"data must be a dict, not {type(data)}")
        forbidden = ['.', '$', '/', ']', '[', '#']
        invalid_keys = list(filter(lambda key: any(char in key for char in forbidden), data.keys()))
        if invalid_keys:
            raise ValueError(f"{data.keys()} must not contain any of the following characters: {forbidden}")

    @staticmethod
    def obtain(ref: dict, keys: list) -> dict:
        """ Traverses the dict to get the data at the specified path.

        Args:
            ref (dict): The dict to traverse.
            keys (list): The list of keys to traverse.

        Returns:
            dict: The data at the specified path.
        """
        try:
            for key in keys:
                ref = ref[key]
            return ref
        except KeyError:
            return {}

    @staticmethod
    def make_dict(keys: list, value: dict) -> dict:
        """ Creates a dict from a list of keys and a value.

        Args:
            keys (list): The list of keys.
            value (dict): The value to set.

        Returns:
            dict: The dict created from the keys and value.
        """
        result = {}
        reference = result
        for key in keys[:-1]:
            reference = reference.setdefault(key, {})
        reference[keys[-1]] = value
        return result

    @staticmethod
    def make_keys(path: str) -> list:
        """ Splits the path into a list of keys.

        Args:
            path (str): The path to split.

        Returns:
            list: The list of keys.
        """
        keys = path.split('/')
        if keys[-1] == '':
            del keys[-1]
        return keys

    def read(self, path: str, shallow: bool = False) -> dict:
        """ Returns the data at the specified path.

        Args:
            path (str): The path to the data.
            shallow (bool, optional): Whether or not to return a shallow copy of the data.

        Returns:
            dict: The data at the specified path.
        """
        if self.ref is not None:
            return self.obtain(self.ref, self.make_keys(path))
        data = db.reference(self.rel_path + path).get(shallow=shallow)
        return data if data else {}

    def update(self, path: str, data: dict) -> None:
        """ Updates the data at the specified path.

        Args:
            path (str): The path to the data.
            data (dict): The data to update.
        """
        self.validate(data)  # throws an exception if the data is not valid.
        if self.ref is not None:
            self.ref = deep_update(self.ref, self.make_dict(self.make_keys(path), data))
        db.reference(self.rel_path + path).update(data)

    def delete(self, path: str, blind: bool = False) -> None:
        """ Deletes the data at the specified path.

        Args:
            path (str): The path to the data.
        """
        db.reference(self.rel_path + path).delete()
        if self.ref is not None and blind is False:
            *path, key = self.make_keys(path)
            del reduce(operator.getitem, path, self.ref)[key]

    def event_printer(self, event) -> None:
        """ Prints out the relevant data whenever a change occurs.

        Example:
            firebase = Firebase(creds)
            firebase.listen('/transactions/account', event_printer)
            ---> prints out the data whenever a change occurs at the specified path.

        """
        print(event.event_type)
        print(event.path)
        print(event.data)
        print(event)

    def listen(self, path: str, listener: object) -> None:
        """ Creates a listener that will print out the relevant data whenever a change occurs.

        Args:
            path (str): The path to the data.
            listener (object): The method that will be receiving the event changes.
        """
        # db.reference(path).listen(self.listener)
        db.reference(self.rel_path + path).listen(listener)
