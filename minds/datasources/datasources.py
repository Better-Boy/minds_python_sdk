from typing import List, Optional, Union

from pydantic import BaseModel, Field

import minds.exceptions as exc

class DatabaseConfig(BaseModel):

    name: str
    engine: str
    description: str
    connection_data: Union[dict, None] = {}
    tables: Union[List[str], None] = []


class Datasource(DatabaseConfig):
    ...


class Datasources:
    def __init__(self, client):
        self.api = client.api

    def create(self, ds_config: DatabaseConfig, replace=False, update=False):
        """
        Create new datasource and return it

        :param ds_config: datasource configuration, properties:
           - name: str, name of datatasource
           - engine: str, type of database handler, for example 'postgres', 'mysql', ...
           - description: str, description of the database. Used by mind to know what data can be got from it.
           - connection_data: dict, optional, credentials to connect to database
           - tables: list of str, optional, list of allowed tables
        :param replace: if true - to remove existing datasource, default is false
        :param update: if true - to update datasourse if exists, default is false
        :return: datasource object
        """

        name = ds_config.name

        if replace:
            try:
                self.get(name)
                self.drop(name)
            except exc.ObjectNotFound:
                ...

        if update:
            self.api.put('/datasources', data=ds_config.model_dump())
        else:
            self.api.post('/datasources', data=ds_config.model_dump())
        return self.get(name)

    def list(self) -> List[Datasource]:
        """
        Returns list of datasources

        :return: iterable datasources
        """

        data = self.api.get('/datasources').json()
        ds_list = []
        for item in data:
            # TODO skip not sql skills
            if item.get('engine') is None:
                continue
            ds_list.append(Datasource(**item))
        return ds_list

    def get(self, name: str) -> Datasource:
        """
        Get datasource by name

        :param name: name of datasource
        :return: datasource object
        """

        data = self.api.get(f'/datasources/{name}').json()

        # TODO skip not sql skills
        if data.get('engine') is None:
            raise exc.ObjectNotSupported(f'Wrong type of datasource: {name}')
        return Datasource(**data)

    def drop(self, name: str):
        """
        Drop datasource by name

        :param name: name of datasource
        """

        self.api.delete(f'/datasources/{name}')
