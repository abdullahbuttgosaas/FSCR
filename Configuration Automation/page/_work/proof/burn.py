"""4c stress: keep every CPU core busy (normal priority) until this process is stopped. Test only."""
import multiprocessing as mp


def spin(_):
    x = 0
    while True:
        x = (x * 31 + 7) % 1000003


if __name__ == "__main__":
    n = mp.cpu_count()
    with mp.Pool(n) as pool:
        print(f"burning {n} cores", flush=True)
        pool.map(spin, range(n))
