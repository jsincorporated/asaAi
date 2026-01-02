from decimal import Decimal

import sqlalchemy as sa
from flask import abort, jsonify, request
from flask_restx import Resource, fields
from pydantic import BaseModel, Field, field_validator

from controllers.console import console_ns
from controllers.console.app.wraps import get_app_model
from controllers.console.wraps import account_initialization_required, setup_required
from core.app.entities.app_invoke_entities import InvokeFrom
from extensions.ext_database import db
from libs.datetime_utils import parse_time_range
from libs.helper import convert_datetime_to_date
from libs.login import current_account_with_tenant, login_required
from models import AppMode

DEFAULT_REF_TEMPLATE_SWAGGER_2_0 = "#/definitions/{model}"


class StatisticTimeRangeQuery(BaseModel):
    start: str | None = Field(default=None, description="Start date (YYYY-MM-DD HH:MM)")
    end: str | None = Field(default=None, description="End date (YYYY-MM-DD HH:MM)")

    @field_validator("start", "end", mode="before")
    @classmethod
    def empty_string_to_none(cls, value: str | None) -> str | None:
        if value == "":
            return None
        return value


console_ns.schema_model(
    StatisticTimeRangeQuery.__name__,
    StatisticTimeRangeQuery.model_json_schema(ref_template=DEFAULT_REF_TEMPLATE_SWAGGER_2_0),
)


@console_ns.route("/apps/<uuid:app_id>/statistics/daily-messages")
class DailyMessageStatistic(Resource):
    @console_ns.doc("get_daily_message_statistics")
    @console_ns.doc(description="Get daily message statistics for an application")
    @console_ns.doc(params={"app_id": "Application ID"})
    @console_ns.expect(console_ns.models[StatisticTimeRangeQuery.__name__])
    @console_ns.response(
        200,
        "Daily message statistics retrieved successfully",
        fields.List(fields.Raw(description="Daily message count data")),
    )
    @get_app_model
    @setup_required
    @login_required
    @account_initialization_required
    def get(self, app_model):
        account, _ = current_account_with_tenant()

        args = StatisticTimeRangeQuery.model_validate(request.args.to_dict(flat=True))  # type: ignore

        converted_created_at = convert_datetime_to_date("created_at")
        sql_query = f"""SELECT
    {converted_created_at} AS date,
    COUNT(*) AS message_count
FROM
    messages
WHERE
    app_id = :app_id
    AND invoke_from != :invoke_from"""
        arg_dict = {"tz": account.timezone, "app_id": app_model.id, "invoke_from": InvokeFrom.DEBUGGER}
        assert account.timezone is not None

        try:
            start_datetime_utc, end_datetime_utc = parse_time_range(args.start, args.end, account.timezone)
        except ValueError as e:
            abort(400, description=str(e))

        if start_datetime_utc:
            sql_query += " AND created_at >= :start"
            arg_dict["start"] = start_datetime_utc

        if end_datetime_utc:
            sql_query += " AND created_at < :end"
            arg_dict["end"] = end_datetime_utc

        sql_query += " GROUP BY date ORDER BY date"

        response_data = []

        with db.engine.begin() as conn:
            rs = conn.execute(sa.text(sql_query), arg_dict)
            for i in rs:
                response_data.append({"date": str(i.date), "message_count": i.message_count})

        return jsonify({"data": response_data})


@console_ns.route("/apps/<uuid:app_id>/statistics/daily-conversations")
class DailyConversationStatistic(Resource):
    @console_ns.doc("get_daily_conversation_statistics")
    @console_ns.doc(description="Get daily conversation statistics for an application")
    @console_ns.doc(params={"app_id": "Application ID"})
    @console_ns.expect(console_ns.models[StatisticTimeRangeQuery.__name__])
    @console_ns.response(
        200,
        "Daily conversation statistics retrieved successfully",
        fields.List(fields.Raw(description="Daily conversation count data")),
    )
    @get_app_model
    @setup_required
    @login_required
    @account_initialization_required
    def get(self, app_model):
        account, _ = current_account_with_tenant()

        args = StatisticTimeRangeQuery.model_validate(request.args.to_dict(flat=True))  # type: ignore

        converted_created_at = convert_datetime_to_date("created_at")
        sql_query = f"""SELECT
    {converted_created_at} AS date,
    COUNT(DISTINCT conversation_id) AS conversation_count
FROM
    messages
WHERE
    app_id = :app_id
    AND invoke_from != :invoke_from"""
        arg_dict = {"tz": account.timezone, "app_id": app_model.id, "invoke_from": InvokeFrom.DEBUGGER}
        assert account.timezone is not None

        try:
            start_datetime_utc, end_datetime_utc = parse_time_range(args.start, args.end, account.timezone)
        except ValueError as e:
            abort(400, description=str(e))

        if start_datetime_utc:
            sql_query += " AND created_at >= :start"
            arg_dict["start"] = start_datetime_utc

        if end_datetime_utc:
            sql_query += " AND created_at < :end"
            arg_dict["end"] = end_datetime_utc

        sql_query += " GROUP BY date ORDER BY date"

        response_data = []
        with db.engine.begin() as conn:
            rs = conn.execute(sa.text(sql_query), arg_dict)
            for i in rs:
                response_data.append({"date": str(i.date), "conversation_count": i.conversation_count})

        return jsonify({"data": response_data})


@console_ns.route("/apps/<uuid:app_id>/statistics/daily-end-users")
class DailyTerminalsStatistic(Resource):
    @console_ns.doc("get_daily_terminals_statistics")
    @console_ns.doc(description="Get daily terminal/end-user statistics for an application")
    @console_ns.doc(params={"app_id": "Application ID"})
    @console_ns.expect(console_ns.models[StatisticTimeRangeQuery.__name__])
    @console_ns.response(
        200,
        "Daily terminal statistics retrieved successfully",
        fields.List(fields.Raw(description="Daily terminal count data")),
    )
    @get_app_model
    @setup_required
    @login_required
    @account_initialization_required
    def get(self, app_model):
        account, _ = current_account_with_tenant()

        args = StatisticTimeRangeQuery.model_validate(request.args.to_dict(flat=True))  # type: ignore

        converted_created_at = convert_datetime_to_date("created_at")
        sql_query = f"""SELECT
    {converted_created_at} AS date,
    COUNT(DISTINCT messages.from_end_user_id) AS terminal_count
FROM
    messages
WHERE
    app_id = :app_id
    AND invoke_from != :invoke_from"""
        arg_dict = {"tz": account.timezone, "app_id": app_model.id, "invoke_from": InvokeFrom.DEBUGGER}
        assert account.timezone is not None

        try:
            start_datetime_utc, end_datetime_utc = parse_time_range(args.start, args.end, account.timezone)
        except ValueError as e:
            abort(400, description=str(e))

        if start_datetime_utc:
            sql_query += " AND created_at >= :start"
            arg_dict["start"] = start_datetime_utc

        if end_datetime_utc:
            sql_query += " AND created_at < :end"
            arg_dict["end"] = end_datetime_utc

        sql_query += " GROUP BY date ORDER BY date"

        response_data = []

        with db.engine.begin() as conn:
            rs = conn.execute(sa.text(sql_query), arg_dict)
            for i in rs:
                response_data.append({"date": str(i.date), "terminal_count": i.terminal_count})

        return jsonify({"data": response_data})


@console_ns.route("/apps/<uuid:app_id>/statistics/token-costs")
class DailyTokenCostStatistic(Resource):
    @console_ns.doc("get_daily_token_cost_statistics")
    @console_ns.doc(description="Get daily token cost statistics for an application")
    @console_ns.doc(params={"app_id": "Application ID"})
    @console_ns.expect(console_ns.models[StatisticTimeRangeQuery.__name__])
    @console_ns.response(
        200,
        "Daily token cost statistics retrieved successfully",
        fields.List(fields.Raw(description="Daily token cost data")),
    )
    @get_app_model
    @setup_required
    @login_required
    @account_initialization_required
    def get(self, app_model):
        account, _ = current_account_with_tenant()

        args = StatisticTimeRangeQuery.model_validate(request.args.to_dict(flat=True))  # type: ignore

        converted_created_at = convert_datetime_to_date("created_at")
        sql_query = f"""SELECT
    {converted_created_at} AS date,
    (SUM(messages.message_tokens) + SUM(messages.answer_tokens)) AS token_count,
    SUM(total_price) AS total_price
FROM
    messages
WHERE
    app_id = :app_id
    AND invoke_from != :invoke_from"""
        arg_dict = {"tz": account.timezone, "app_id": app_model.id, "invoke_from": InvokeFrom.DEBUGGER}
        assert account.timezone is not None

        try:
            start_datetime_utc, end_datetime_utc = parse_time_range(args.start, args.end, account.timezone)
        except ValueError as e:
            abort(400, description=str(e))

        if start_datetime_utc:
            sql_query += " AND created_at >= :start"
            arg_dict["start"] = start_datetime_utc

        if end_datetime_utc:
            sql_query += " AND created_at < :end"
            arg_dict["end"] = end_datetime_utc

        sql_query += " GROUP BY date ORDER BY date"

        response_data = []

        with db.engine.begin() as conn:
            rs = conn.execute(sa.text(sql_query), arg_dict)
            for i in rs:
                response_data.append(
                    {"date": str(i.date), "token_count": i.token_count, "total_price": i.total_price, "currency": "USD"}
                )

        return jsonify({"data": response_data})


@console_ns.route("/apps/<uuid:app_id>/statistics/average-session-interactions")
class AverageSessionInteractionStatistic(Resource):
    @console_ns.doc("get_average_session_interaction_statistics")
    @console_ns.doc(description="Get average session interaction statistics for an application")
    @console_ns.doc(params={"app_id": "Application ID"})
    @console_ns.expect(console_ns.models[StatisticTimeRangeQuery.__name__])
    @console_ns.response(
        200,
        "Average session interaction statistics retrieved successfully",
        fields.List(fields.Raw(description="Average session interaction data")),
    )
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT])
    def get(self, app_model):
        account, _ = current_account_with_tenant()

        args = StatisticTimeRangeQuery.model_validate(request.args.to_dict(flat=True))  # type: ignore

        converted_created_at = convert_datetime_to_date("c.created_at")
        sql_query = f"""SELECT
    {converted_created_at} AS date,
    AVG(subquery.message_count) AS interactions
FROM
    (
        SELECT
            m.conversation_id,
            COUNT(m.id) AS message_count
        FROM
            conversations c
        JOIN
            messages m
            ON c.id = m.conversation_id
        WHERE
            c.app_id = :app_id
            AND m.invoke_from != :invoke_from"""
        arg_dict = {"tz": account.timezone, "app_id": app_model.id, "invoke_from": InvokeFrom.DEBUGGER}
        assert account.timezone is not None

        try:
            start_datetime_utc, end_datetime_utc = parse_time_range(args.start, args.end, account.timezone)
        except ValueError as e:
            abort(400, description=str(e))

        if start_datetime_utc:
            sql_query += " AND c.created_at >= :start"
            arg_dict["start"] = start_datetime_utc

        if end_datetime_utc:
            sql_query += " AND c.created_at < :end"
            arg_dict["end"] = end_datetime_utc

        sql_query += """
        GROUP BY m.conversation_id
    ) subquery
LEFT JOIN
    conversations c
    ON c.id = subquery.conversation_id
GROUP BY
    date
ORDER BY
    date"""

        response_data = []

        with db.engine.begin() as conn:
            rs = conn.execute(sa.text(sql_query), arg_dict)
            for i in rs:
                response_data.append(
                    {"date": str(i.date), "interactions": float(i.interactions.quantize(Decimal("0.01")))}
                )

        return jsonify({"data": response_data})


@console_ns.route("/apps/<uuid:app_id>/statistics/user-satisfaction-rate")
class UserSatisfactionRateStatistic(Resource):
    @console_ns.doc("get_user_satisfaction_rate_statistics")
    @console_ns.doc(description="Get user satisfaction rate statistics for an application")
    @console_ns.doc(params={"app_id": "Application ID"})
    @console_ns.expect(console_ns.models[StatisticTimeRangeQuery.__name__])
    @console_ns.response(
        200,
        "User satisfaction rate statistics retrieved successfully",
        fields.List(fields.Raw(description="User satisfaction rate data")),
    )
    @get_app_model
    @setup_required
    @login_required
    @account_initialization_required
    def get(self, app_model):
        account, _ = current_account_with_tenant()

        args = StatisticTimeRangeQuery.model_validate(request.args.to_dict(flat=True))  # type: ignore

        converted_created_at = convert_datetime_to_date("m.created_at")
        sql_query = f"""SELECT
    {converted_created_at} AS date,
    COUNT(m.id) AS message_count,
    COUNT(mf.id) AS feedback_count
FROM
    messages m
LEFT JOIN
    message_feedbacks mf
    ON mf.message_id=m.id AND mf.rating='like'
WHERE
    m.app_id = :app_id
    AND m.invoke_from != :invoke_from"""
        arg_dict = {"tz": account.timezone, "app_id": app_model.id, "invoke_from": InvokeFrom.DEBUGGER}
        assert account.timezone is not None

        try:
            start_datetime_utc, end_datetime_utc = parse_time_range(args.start, args.end, account.timezone)
        except ValueError as e:
            abort(400, description=str(e))

        if start_datetime_utc:
            sql_query += " AND m.created_at >= :start"
            arg_dict["start"] = start_datetime_utc

        if end_datetime_utc:
            sql_query += " AND m.created_at < :end"
            arg_dict["end"] = end_datetime_utc

        sql_query += " GROUP BY date ORDER BY date"

        response_data = []

        with db.engine.begin() as conn:
            rs = conn.execute(sa.text(sql_query), arg_dict)
            for i in rs:
                response_data.append(
                    {
                        "date": str(i.date),
                        "rate": round((i.feedback_count * 1000 / i.message_count) if i.message_count > 0 else 0, 2),
                    }
                )

        return jsonify({"data": response_data})


@console_ns.route("/apps/<uuid:app_id>/statistics/average-response-time")
class AverageResponseTimeStatistic(Resource):
    @console_ns.doc("get_average_response_time_statistics")
    @console_ns.doc(description="Get average response time statistics for an application")
    @console_ns.doc(params={"app_id": "Application ID"})
    @console_ns.expect(console_ns.models[StatisticTimeRangeQuery.__name__])
    @console_ns.response(
        200,
        "Average response time statistics retrieved successfully",
        fields.List(fields.Raw(description="Average response time data")),
    )
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=AppMode.COMPLETION)
    def get(self, app_model):
        account, _ = current_account_with_tenant()

        args = StatisticTimeRangeQuery.model_validate(request.args.to_dict(flat=True))  # type: ignore

        converted_created_at = convert_datetime_to_date("created_at")
        sql_query = f"""SELECT
    {converted_created_at} AS date,
    AVG(provider_response_latency) AS latency
FROM
    messages
WHERE
    app_id = :app_id
    AND invoke_from != :invoke_from"""
        arg_dict = {"tz": account.timezone, "app_id": app_model.id, "invoke_from": InvokeFrom.DEBUGGER}
        assert account.timezone is not None

        try:
            start_datetime_utc, end_datetime_utc = parse_time_range(args.start, args.end, account.timezone)
        except ValueError as e:
            abort(400, description=str(e))

        if start_datetime_utc:
            sql_query += " AND created_at >= :start"
            arg_dict["start"] = start_datetime_utc

        if end_datetime_utc:
            sql_query += " AND created_at < :end"
            arg_dict["end"] = end_datetime_utc

        sql_query += " GROUP BY date ORDER BY date"

        response_data = []

        with db.engine.begin() as conn:
            rs = conn.execute(sa.text(sql_query), arg_dict)
            for i in rs:
                response_data.append({"date": str(i.date), "latency": round(i.latency * 1000, 4)})

        return jsonify({"data": response_data})


@console_ns.route("/apps/<uuid:app_id>/statistics/tokens-per-second")
class TokensPerSecondStatistic(Resource):
    @console_ns.doc("get_tokens_per_second_statistics")
    @console_ns.doc(description="Get tokens per second statistics for an application")
    @console_ns.doc(params={"app_id": "Application ID"})
    @console_ns.expect(console_ns.models[StatisticTimeRangeQuery.__name__])
    @console_ns.response(
        200,
        "Tokens per second statistics retrieved successfully",
        fields.List(fields.Raw(description="Tokens per second data")),
    )
    @get_app_model
    @setup_required
    @login_required
    @account_initialization_required
    def get(self, app_model):
        account, _ = current_account_with_tenant()
        args = StatisticTimeRangeQuery.model_validate(request.args.to_dict(flat=True))  # type: ignore

        converted_created_at = convert_datetime_to_date("created_at")
        sql_query = f"""SELECT
    {converted_created_at} AS date,
    CASE
        WHEN SUM(provider_response_latency) = 0 THEN 0
        ELSE (SUM(answer_tokens) / SUM(provider_response_latency))
    END as tokens_per_second
FROM
    messages
WHERE
    app_id = :app_id
    AND invoke_from != :invoke_from"""
        arg_dict = {"tz": account.timezone, "app_id": app_model.id, "invoke_from": InvokeFrom.DEBUGGER}
        assert account.timezone is not None

        try:
            start_datetime_utc, end_datetime_utc = parse_time_range(args.start, args.end, account.timezone)
        except ValueError as e:
            abort(400, description=str(e))

        if start_datetime_utc:
            sql_query += " AND created_at >= :start"
            arg_dict["start"] = start_datetime_utc

        if end_datetime_utc:
            sql_query += " AND created_at < :end"
            arg_dict["end"] = end_datetime_utc

        sql_query += " GROUP BY date ORDER BY date"

        response_data = []

        with db.engine.begin() as conn:
            rs = conn.execute(sa.text(sql_query), arg_dict)
            for i in rs:
                response_data.append({"date": str(i.date), "tps": round(i.tokens_per_second, 4)})

        return jsonify({"data": response_data})


@console_ns.route("/apps/<uuid:app_id>/statistics/conversations")
class ConversationStatisticsApi(Resource):
    """Get conversation statistics for ASA analytics."""

    @console_ns.doc("get_conversation_statistics")
    @console_ns.doc(description="Get conversation statistics including total count and breakdown")
    @console_ns.doc(params={"app_id": "Application ID"})
    @console_ns.expect(console_ns.models[StatisticTimeRangeQuery.__name__])
    @console_ns.response(200, "Conversation statistics retrieved successfully")
    @get_app_model
    @setup_required
    @login_required
    @account_initialization_required
    def get(self, app_model):
        """Get conversation statistics for an app."""
        account, _ = current_account_with_tenant()
        args = StatisticTimeRangeQuery.model_validate(request.args.to_dict(flat=True))  # type: ignore

        assert account.timezone is not None

        try:
            start_datetime_utc, end_datetime_utc = parse_time_range(args.start, args.end, account.timezone)
        except ValueError as e:
            abort(400, description=str(e))

        # Total conversations
        total_sql = """SELECT COUNT(DISTINCT id) AS total_count FROM conversations WHERE app_id = :app_id"""
        arg_dict = {"app_id": app_model.id}

        if start_datetime_utc:
            total_sql += " AND created_at >= :start"
            arg_dict["start"] = start_datetime_utc

        if end_datetime_utc:
            total_sql += " AND created_at < :end"
            arg_dict["end"] = end_datetime_utc

        # Messages per conversation
        messages_sql = """
        SELECT
            c.id as conversation_id,
            COUNT(m.id) AS message_count,
            SUM(m.message_tokens + m.answer_tokens) AS total_tokens
        FROM conversations c
        LEFT JOIN messages m ON c.id = m.conversation_id
        WHERE c.app_id = :app_id"""

        if start_datetime_utc:
            messages_sql += " AND c.created_at >= :start"

        if end_datetime_utc:
            messages_sql += " AND c.created_at < :end"

        messages_sql += " GROUP BY c.id"

        response_data: dict[str, int | float] = {
            "total_conversations": 0,
            "total_messages": 0,
            "total_tokens": 0,
            "avg_messages_per_conversation": 0.0,
        }

        with db.engine.begin() as conn:
            # Get total count
            rs = conn.execute(sa.text(total_sql), arg_dict)
            row = rs.fetchone()
            if row:
                response_data["total_conversations"] = row.total_count

            # Get messages stats
            rs = conn.execute(sa.text(messages_sql), arg_dict)
            total_messages = 0
            total_tokens = 0
            conv_count = 0
            for row in rs:
                conv_count += 1
                total_messages += row.message_count or 0
                total_tokens += row.total_tokens or 0

            response_data["total_messages"] = total_messages
            response_data["total_tokens"] = total_tokens
            if conv_count > 0:
                response_data["avg_messages_per_conversation"] = round(total_messages / conv_count, 2)

        return jsonify({"data": response_data})


@console_ns.route("/apps/<uuid:app_id>/statistics/workflow-runs")
class WorkflowRunStatisticsApi(Resource):
    """Get workflow run statistics for ASA analytics."""

    @console_ns.doc("get_workflow_run_statistics")
    @console_ns.doc(description="Get workflow run statistics including success/failure rates")
    @console_ns.doc(params={"app_id": "Application ID"})
    @console_ns.expect(console_ns.models[StatisticTimeRangeQuery.__name__])
    @console_ns.response(200, "Workflow run statistics retrieved successfully")
    @get_app_model(mode=[AppMode.WORKFLOW, AppMode.ADVANCED_CHAT])
    @setup_required
    @login_required
    @account_initialization_required
    def get(self, app_model):
        """Get workflow run statistics for an app."""
        account, _ = current_account_with_tenant()
        args = StatisticTimeRangeQuery.model_validate(request.args.to_dict(flat=True))  # type: ignore

        assert account.timezone is not None

        try:
            start_datetime_utc, end_datetime_utc = parse_time_range(args.start, args.end, account.timezone)
        except ValueError as e:
            abort(400, description=str(e))

        sql_query = """
        SELECT
            COUNT(*) AS total_runs,
            SUM(CASE WHEN status = 'succeeded' THEN 1 ELSE 0 END) AS succeeded_count,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed_count,
            SUM(CASE WHEN status = 'stopped' THEN 1 ELSE 0 END) AS stopped_count,
            SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) AS running_count,
            AVG(elapsed_time) AS avg_elapsed_time,
            SUM(total_tokens) AS total_tokens,
            SUM(total_steps) AS total_steps
        FROM workflow_runs
        WHERE app_id = :app_id"""

        arg_dict = {"app_id": app_model.id}

        if start_datetime_utc:
            sql_query += " AND created_at >= :start"
            arg_dict["start"] = start_datetime_utc

        if end_datetime_utc:
            sql_query += " AND created_at < :end"
            arg_dict["end"] = end_datetime_utc

        response_data: dict[str, int | float] = {
            "total_runs": 0,
            "succeeded_count": 0,
            "failed_count": 0,
            "stopped_count": 0,
            "running_count": 0,
            "success_rate": 0.0,
            "avg_elapsed_time": 0.0,
            "total_tokens": 0,
            "total_steps": 0,
        }

        with db.engine.begin() as conn:
            rs = conn.execute(sa.text(sql_query), arg_dict)
            row = rs.fetchone()
            if row and row.total_runs:
                response_data["total_runs"] = row.total_runs
                response_data["succeeded_count"] = row.succeeded_count or 0
                response_data["failed_count"] = row.failed_count or 0
                response_data["stopped_count"] = row.stopped_count or 0
                response_data["running_count"] = row.running_count or 0
                response_data["avg_elapsed_time"] = round(float(row.avg_elapsed_time or 0), 4)
                response_data["total_tokens"] = row.total_tokens or 0
                response_data["total_steps"] = row.total_steps or 0
                if row.total_runs > 0:
                    response_data["success_rate"] = round((row.succeeded_count or 0) / row.total_runs * 100, 2)

        return jsonify({"data": response_data})
