
from flask import request
from flask_login import current_user
from flask_restful import Resource, reqparse

from controllers.console import api
from controllers.console.app.wraps import get_app_model
from controllers.console.setup import setup_required
from controllers.console.wraps import account_initialization_required
from events.app_event import app_model_config_was_updated
from extensions.ext_database import db
from libs.login import login_required
from models.model import AppModelConfig, AppMode
from services.app_model_config_service import AppModelConfigService


class ModelConfigResource(Resource):

    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.AGENT_CHAT, AppMode.CHAT, AppMode.COMPLETION])
    def post(self, app_model):
        """Modify app model config"""
        # validate config
        model_configuration = AppModelConfigService.validate_configuration(
            tenant_id=current_user.current_tenant_id,
            config=request.json,
            app_mode=AppMode.value_of(app_model.mode)
        )

        new_app_model_config = AppModelConfig(
            app_id=app_model.id,
        )
        new_app_model_config = new_app_model_config.from_model_config_dict(model_configuration)

        db.session.add(new_app_model_config)
        db.session.flush()

        app_model.app_model_config_id = new_app_model_config.id
        db.session.commit()

        app_model_config_was_updated.send(
            app_model,
            app_model_config=new_app_model_config
        )

        return {'result': 'success'}


class FeaturesResource(Resource):

        @setup_required
        @login_required
        @account_initialization_required
        @get_app_model(mode=[AppMode.ADVANCED_CHAT, AppMode.WORKFLOW])
        def put(self, app_model):
            """Get app features"""
            parser = reqparse.RequestParser()
            parser.add_argument('features', type=dict, required=True, nullable=False, location='json')
            args = parser.parse_args()

            model_configuration = AppModelConfigService.validate_features(
                tenant_id=current_user.current_tenant_id,
                config=args.get('features'),
                app_mode=AppMode.value_of(app_model.mode)
            )

            # update config
            app_model_config = app_model.app_model_config
            app_model_config.from_model_config_dict(model_configuration)
            db.session.commit()

            app_model_config_was_updated.send(
                app_model,
                app_model_config=app_model_config
            )

            return {
                'result': 'success'
            }


api.add_resource(ModelConfigResource, '/apps/<uuid:app_id>/model-config')
api.add_resource(FeaturesResource, '/apps/<uuid:app_id>/features')
