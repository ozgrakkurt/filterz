import hypersync
from hypersync import TransactionField, ClientConfig, Query, TransactionSelection, FieldSelection, StreamConfig
import asyncio

DATA_FILE_PATH = "addr.data"
INDEX_FILE_PATH = "addr.index"
TOTAL_TX = 10000000
TX_PER_SECTION = 100000

async def main():
    client = hypersync.HypersyncClient(ClientConfig())
    query = Query(
        from_block=18123123,
        transactions=[TransactionSelection()],
        field_selection=FieldSelection(
            transaction=[
                TransactionField.FROM,
            ]
        ),
    )

    receiver = await client.stream_arrow(query, StreamConfig())

    data_file = open(DATA_FILE_PATH, 'wb')
    index_file = open(INDEX_FILE_PATH, 'w')

    num_addrs = 0
    num_tx = 0
    total_num_tx = 0

    while True:
        res = await receiver.recv()

        if res is None:
            index_file.write(' ' + str(num_addrs))
            break

        for addr in res.data.transactions.column('from'):
            num_tx += 1
            total_num_tx += 1
            if addr is not None:
                num_addrs += 1
                data_file.write(addr.as_buffer())

        if total_num_tx >= TOTAL_TX:
            index_file.write(' ' + str(num_addrs))
            break
        elif num_tx >= TX_PER_SECTION:
            index_file.write(' ' + str(num_addrs))
            num_addrs = 0
            num_tx = 0

    data_file.close()
    index_file.close()

asyncio.run(main())
