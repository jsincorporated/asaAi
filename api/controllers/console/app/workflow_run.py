import decimal
from typing import cast

from flask_login import current_user
from flask_restful import Resource, marshal_with, reqparse
from flask_restful.inputs import int_range

from controllers.console import api
from controllers.console.app.wraps import get_app_model
from controllers.console.wraps import account_initialization_required, setup_required
from fields.workflow_run_fields import (
    advanced_chat_workflow_run_pagination_fields,
    workflow_run_detail_fields,
    workflow_run_node_execution_list_fields,
    workflow_run_pagination_fields,
    workflow_run_statistics_fields,
)
from libs.helper import uuid_value
from libs.login import login_required
from models import Account, App, AppMode, EndUser
from services.workflow_run_service import WorkflowRunService



class AdvancedChatAppWorkflowRunListApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.ADVANCED_CHAT])
    @marshal_with(advanced_chat_workflow_run_pagination_fields)
    def get(self, app_model: App):
        """
        Get advanced chat app workflow run list
        """
        parser = reqparse.RequestParser()
        parser.add_argument("last_id", type=uuid_value, location="args")
        parser.add_argument("limit", type=int_range(1, 100), required=False, default=20, location="args")
        args = parser.parse_args()

        workflow_run_service = WorkflowRunService()
        result = workflow_run_service.get_paginate_advanced_chat_workflow_runs(app_model=app_model, args=args)

        return result


class WorkflowRunListApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.ADVANCED_CHAT, AppMode.WORKFLOW])
    @marshal_with(workflow_run_pagination_fields)
    def get(self, app_model: App):
        """
        Get workflow run list
        """
        parser = reqparse.RequestParser()
        parser.add_argument("last_id", type=uuid_value, location="args")
        parser.add_argument("limit", type=int_range(1, 100), required=False, default=20, location="args")
        args = parser.parse_args()

        workflow_run_service = WorkflowRunService()
        result = workflow_run_service.get_paginate_workflow_runs(app_model=app_model, args=args)

        return result


class WorkflowRunDetailApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.ADVANCED_CHAT, AppMode.WORKFLOW])
    @marshal_with(workflow_run_detail_fields)
    def get(self, app_model: App, run_id):
        """
        Get workflow run detail
        """
        run_id = str(run_id)

        workflow_run_service = WorkflowRunService()
        workflow_run = workflow_run_service.get_workflow_run(app_model=app_model, run_id=run_id)

        return workflow_run


class WorkflowRunNodeExecutionListApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.ADVANCED_CHAT, AppMode.WORKFLOW])
    @marshal_with(workflow_run_node_execution_list_fields)
    def get(self, app_model: App, run_id):
        """
        Get workflow run node execution list
        """
        run_id = str(run_id)

        workflow_run_service = WorkflowRunService()
        user = cast("Account | EndUser", current_user)
        node_executions = workflow_run_service.get_workflow_run_node_executions(
            app_model=app_model,
            run_id=run_id,
            user=user,
        )

        return {"data": node_executions}

# Custom ASA endpoint
class WorkflowRunStatisticsApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.ADVANCED_CHAT, AppMode.WORKFLOW])
    @marshal_with(workflow_run_statistics_fields)
    def get(self, app_model: App, run_id):
        """
        Get workflow run statistics
        """
        run_id = str(run_id)

        workflow_run_service = WorkflowRunService()
        user = cast("Account | EndUser", current_user)
        node_executions = workflow_run_service.get_workflow_run_node_executions(
            app_model=app_model,
            run_id=run_id,
            user=user,
        )

        total_tokens = 0
        total_price = decimal.Decimal(0.0)
        currency = "USD"

        for node_execution in node_executions:
            metadata = node_execution.execution_metadata_dict
            if metadata and "total_tokens" in metadata:
                total_tokens += metadata["total_tokens"]
            if metadata and "total_price" in metadata:
                total_price += decimal.Decimal(str(metadata["total_price"]))
            if metadata and "currency" in metadata:
                currency = metadata["currency"]

        return {
            "total_tokens": total_tokens,
            "total_price": float(total_price),
            "currency": currency,
        }


api.add_resource(AdvancedChatAppWorkflowRunListApi, "/apps/<uuid:app_id>/advanced-chat/workflow-runs")
api.add_resource(WorkflowRunListApi, "/apps/<uuid:app_id>/workflow-runs")
api.add_resource(WorkflowRunDetailApi, "/apps/<uuid:app_id>/workflow-runs/<uuid:run_id>")
api.add_resource(WorkflowRunNodeExecutionListApi, "/apps/<uuid:app_id>/workflow-runs/<uuid:run_id>/node-executions")
api.add_resource(WorkflowRunStatisticsApi, "/apps/<uuid:app_id>/workflow-runs/<uuid:run_id>/statistics")
