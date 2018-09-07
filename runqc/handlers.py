import logging
log = logging.getLogger()

# orig from: http://flask.pocoo.org/snippets/127/
def dump_environment(e, **extra):
    """dump enivronment variables on request exception"""
    # add all necessary log info here
    log.info("dumping request: %s", request)
    log.info("dumping request args: %s", request.args)
    log.info("dumping session: %s", session)


from flask import got_request_exception
got_request_exception.connect(dump_environment)
