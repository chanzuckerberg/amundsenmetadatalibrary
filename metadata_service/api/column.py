# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import json
from http import HTTPStatus
from typing import Iterable, Mapping, Union

from flasgger import swag_from
from flask import request
from flask_restful import Resource, reqparse

from metadata_service.exception import NotFoundException
from metadata_service.proxy import get_proxy_client

from metadata_service.api.badge import BadgeCommon
from metadata_service.entity.resource_type import ResourceType


class ColumnDescriptionAPI(Resource):
    """
    ColumnDescriptionAPI supports PUT and GET operations to upsert column description
    """

    def __init__(self) -> None:
        self.client = get_proxy_client()
        super(ColumnDescriptionAPI, self).__init__()

    @swag_from('swagger_doc/column/description_put.yml')
    def put(self,
            table_uri: str,
            column_name: str) -> Iterable[Union[dict, tuple, int, None]]:
        """
        Updates column description (passed as a request body)
        :param table_uri:
        :param column_name:
        :return:
        """
        try:
            description = json.loads(request.data).get('description')
            self.client.put_column_description(table_uri=table_uri,
                                               column_name=column_name,
                                               description=description)
            return None, HTTPStatus.OK

        except NotFoundException:
            msg = 'table_uri {} with column {} does not exist'.format(table_uri, column_name)
            return {'message': msg}, HTTPStatus.NOT_FOUND

    @swag_from('swagger_doc/column/description_get.yml')
    def get(self, table_uri: str, column_name: str) -> Union[tuple, int, None]:
        """
        Gets column descriptions in Neo4j
        """
        try:
            description = self.client.get_column_description(table_uri=table_uri,
                                                             column_name=column_name)

            return {'description': description}, HTTPStatus.OK

        except NotFoundException:
            msg = 'table_uri {} with column {} does not exist'.format(table_uri, column_name)
            return {'message': msg}, HTTPStatus.NOT_FOUND

        except Exception:
            return {'message': 'Internal server error!'}, HTTPStatus.INTERNAL_SERVER_ERROR


class ColumnBadgeAPI(Resource):
    def __init__(self) -> None:
        self.client = get_proxy_client()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('category', type=str, required=True)
        super(ColumnBadgeAPI, self).__init__()

        self._badge_common = BadgeCommon(client=self.client)

    @swag_from('swagger_doc/badge/badge_put.yml')
    def put(self, id: str, badge: str, column_name: str) -> Iterable[Union[Mapping, int, None]]:
        args = self.parser.parse_args()
        category = args.get('category', '')

        return self._badge_common.put(id=id,
                                      resource_type=ResourceType.Column,
                                      badge_name=badge,
                                      category=category,
                                      column_name=column_name)

    @swag_from('swagger_doc/badge/badge_delete.yml')
    def delete(self, id: str, badge: str, column_name: str) -> Iterable[Union[Mapping, int, None]]:
        args = self.parser.parse_args()
        category = args.get('category', '')

        return self._badge_common.delete(id=id,
                                         resource_type=ResourceType.Column,
                                         badge_name=badge,
                                         category=category,
                                         column_name=column_name)
