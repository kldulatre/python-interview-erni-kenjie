# Import all the models, so that Base has them before being
# imported by Alembic or used by main
from app.db.base_class import Base  # noqa
from app.models.exchange_rate_model import ExchangeRateModel  # noqa
from app.models.transaction_model import TransactionModel  # noqa
