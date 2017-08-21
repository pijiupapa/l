from raven import Client
from raven.transport.http import HTTPTransport

client = Client('https://39d6c3f5a3224377ae92250890ccfbec:e0d30deaa58d429784c7a2f4e36d38b6@sentry.io/101387', transport=HTTPTransport)
