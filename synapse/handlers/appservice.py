# -*- coding: utf-8 -*-
# Copyright 2015 OpenMarket Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from twisted.internet import defer

from ._base import BaseHandler
from synapse.api.errors import Codes, StoreError, SynapseError

import logging


logger = logging.getLogger(__name__)


class ApplicationServicesHandler(BaseHandler):

    def __init__(self, hs):
        super(ApplicationServicesHandler, self).__init__(hs)

    @defer.inlineCallbacks
    def register(self, app_service):
        logger.info("Register -> %s", app_service)
        # check the token is recognised
        try:
            stored_service = yield self.store.get_app_service_by_token(
                app_service.token
            )
            if not stored_service:
                raise StoreError(404, "Application service not found")
        except StoreError:
            raise SynapseError(
                403, "Unrecognised application services token. "
                "Consult the home server admin.",
                errcode=Codes.FORBIDDEN
            )
        logger.info("Updating application service info...")
        yield self.store.update_app_service(app_service)

    def unregister(self, token):
        logger.info("Unregister as_token=%s", token)
        yield self.store.unregister_app_service(token)

    def get_services_for_event(self, event):
        """Retrieve a list of application services interested in this event.

        Args:
            event(Event): The event to check.
        Returns:
            list<ApplicationService>: A list of services interested in this
            event based on the service regex.
        """
        # We need to know the aliases associated with this event.room_id, if any
        alias_list = []  # TODO

        interested_list = [
            s for s in self.store.get_app_services() if (
                s.is_interested(event, alias_list)
            )
        ]
        return interested_list

    def notify_interested_services(self, event):
        """Notifies (pushes) all application services interested in this event.

        Pushing is done asynchronously, so this method won't block for any
        prolonged length of time.

        Args:
            event(Event): The event to push out to interested services.
        """
        # TODO: Gather interested services
        #         get_services_for_event(event) <-- room IDs and user IDs
        #         Get a list of room aliases. Check regex.
        # TODO: If unknown user: poke User Query API.
        # TODO: If unknown room alias: poke Room Alias Query API.

        # TODO: Fork off pushes to these services - XXX First cut, best effort
        pass
