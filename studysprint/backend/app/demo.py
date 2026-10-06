"""Demo content: a small Operating Systems lecture rendered as a real PDF."""

import textwrap

SAMPLE_FILENAME = "os-lecture-week3.pdf"

SAMPLE_PAGES: list[tuple[str, str]] = [
    (
        "Processes and Threads",
        "A process is a program in execution with its own address space, registers and "
        "open files. A thread is the smallest unit of execution that the scheduler can run "
        "inside a process. Threads of the same process share memory and open files, which "
        "makes communication cheap but requires synchronization. A context switch saves the "
        "state of the running process and restores the state of the next one.",
    ),
    (
        "CPU Scheduling",
        "The scheduler decides which ready process runs next on the CPU. Round robin gives "
        "each process a fixed time quantum and moves it to the back of the ready queue when "
        "the quantum expires. Shortest job first minimizes average waiting time but can "
        "starve long jobs. Starvation is a situation where a process waits indefinitely "
        "because other processes are always preferred.",
    ),
    (
        "Virtual Memory and Paging",
        "Virtual memory is a technique that gives each process the illusion of a large, "
        "private address space. Paging divides memory into fixed-size pages and frames, and "
        "the page table maps virtual pages to physical frames. A page fault occurs when a "
        "process accesses a page that is not in physical memory, so the operating system "
        "loads it from disk. Thrashing happens when the system spends more time handling "
        "page faults than running processes.",
    ),
    (
        "Deadlocks",
        "A deadlock is a state where a set of processes are each waiting for a resource held "
        "by another process in the set. Four conditions must hold for deadlock: mutual "
        "exclusion, hold and wait, no preemption and circular wait. Deadlock prevention "
        "breaks at least one of these conditions, for example by ordering resource requests. "
        "The banker's algorithm avoids deadlock by only granting requests that keep the "
        "system in a safe state.",
    ),
]


def make_pdf(pages: list[list[str]]) -> bytes:
    """Write a minimal multi-page PDF (Helvetica text) without third-party dependencies."""
    n = len(pages)
    page_ids = [4 + 2 * i for i in range(n)]
    kids = " ".join(f"{p} 0 R" for p in page_ids)
    objs: dict[int, bytes] = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: f"<< /Type /Pages /Kids [{kids}] /Count {n} >>".encode(),
        3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    }
    for pid, lines in zip(page_ids, pages, strict=True):
        objs[pid] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {pid + 1} 0 R >>"
        ).encode()
        ops = ["BT", "/F1 11 Tf", "15 TL", "56 740 Td"]
        for line in lines:
            esc = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            ops.append(f"({esc}) Tj T*")
        ops.append("ET")
        stream = "\n".join(ops).encode("latin-1")
        objs[pid + 1] = b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream"

    out = bytearray(b"%PDF-1.4\n")
    offsets: dict[int, int] = {}
    for oid in sorted(objs):
        offsets[oid] = len(out)
        out += f"{oid} 0 obj\n".encode() + objs[oid] + b"\nendobj\n"
    xref = len(out)
    size = max(objs) + 1
    out += f"xref\n0 {size}\n0000000000 65535 f \n".encode()
    for oid in range(1, size):
        out += f"{offsets[oid]:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {size} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(out)


def sample_pdf() -> bytes:
    return make_pdf([[title, ""] + textwrap.wrap(body, 88) for title, body in SAMPLE_PAGES])
