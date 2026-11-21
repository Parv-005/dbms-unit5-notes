# Schedule definitions.  Line format:  "T1: op   # remark"   (prefix op with ! = problem row, * = key row)
# Compact format: string starting with '@'  e.g.  "@r1(X); w2(X); c1"

SCHED = {}


def S(name, s, **kw):
    SCHED[name] = dict(s=s, **kw)


# ---------------------------------------------------------------- Section 1
S('debit', '''
T1: read(X)        # X = 4000 is copied from disk into the buffer
T1: X = X − 500    # buffer now holds 3500 (database still 4000)
T1: write(X)       # 3500 is written back; final X = 3500
''', cap='Debit transaction T1 (initially X = 4000)')

S('transfer', '''
T: read(A)        # A = 600
T: A = A − 100    # local A = 500
T: write(A)       # database A = 500
T: read(B)        # B = 300
T: B = B + 100    # local B = 400
T: write(B)       # database B = 400
T: commit         # A + B = 900 before and after
''', cap='Transaction T: transfer ₹100 from A to B (A = 600, B = 300)')

# ---------------------------------------------------------------- Section 4/6 basic schedules
S('serialA', '''
T1: read(X)
T1: X = X − N
T1: write(X)
T1: read(Y)
T1: Y = Y + N
T1: write(Y)
T2: read(X)
T2: X = X + M
T2: write(X)
''', cap='Schedule A — serial (T1 completely, then T2)')

S('serialB', '''
T2: read(X)
T2: X = X + M
T2: write(X)
T1: read(X)
T1: X = X − N
T1: write(X)
T1: read(Y)
T1: Y = Y + N
T1: write(Y)
''', cap='Schedule B — serial (T2 completely, then T1)')

S('nonserialC', '''
T1: read(X)
T1: X = X − N
T2: read(X)
T2: X = X + M
T1: write(X)
T1: read(Y)
T2: *write(X)    # overwrites T1's write — T1's update is lost
T1: Y = Y + N
T1: write(Y)
''', cap='Schedule C — non-serial (interleaved)')

S('nonserialD', '''
T1: read(X)
T1: X = X − N
T1: write(X)
T2: read(X)
T2: X = X + M
T2: write(X)
T1: read(Y)
T1: Y = Y + N
T1: write(Y)
''', cap='Schedule D — non-serial, but gives the same result as serial A')

# ---------------------------------------------------------------- Section 5 problems
S('lost', '''
T1: read(X)       # T1 sees X = 10
T2: read(X)       # T2 also sees X = 10
T1: X = X + 10    # T1 local X = 20
T1: write(X)      # database X = 20
T2: X = X + 20    # T2 local X = 10 + 20 = 30 (stale value used!)
T2: !write(X)     # database X = 30 ✗  (should be 40; T1's +10 is LOST)
''', cap='Lost Update (W–W conflict). Initially X = 10.')

S('dirty', '''
T1: read(X)       # X = 10
T1: X = X + 10
T1: write(X)      # database X = 20 (not committed yet)
T2: !read(X)      # T2 reads 20 → DIRTY READ
T2: X = X * 2
T2: write(X)      # T2 writes 40 based on dirty value
T2: commit
T1: !failure → rollback   # X restored to 10, but T2 already used 20 and committed
''', cap='Dirty Read / Temporary Update (W–R conflict). Initially X = 10.')

S('unrep', '''
T2: read(X)       # T2 sees X = 10
T1: read(X)
T1: X = X + 10
T1: write(X)      # X = 20
T1: commit
T2: !read(X)      # T2 now sees X = 20 — same item, different value
''', cap='Unrepeatable (Non-repeatable) Read (R–W conflict). Initially X = 10.')

S('phantom', '''
T1: SELECT COUNT(*) FROM Student WHERE dept = 'IT'   # result = 50
T2: INSERT INTO Student VALUES (101, 'Riya', 'IT')
T2: commit
T1: !SELECT COUNT(*) FROM Student WHERE dept = 'IT'  # result = 51 — a "phantom" row appeared
''', cap='Phantom Read. The set of rows satisfying the condition changes.')

S('phantom_lec', '''
T1: read(X)
T2: read(X)
T1: delete(X)
T2: !read(X)     # X no longer exists — row "vanished"
''', cap='Phantom read as written in class (row deleted between two reads)')

S('incsum', '''
T1: sum = 0
T1: read(A)      # A = 100 → sum = 100
T1: sum = sum + A
T2: read(X)      # X = 50
T2: X = X − 10
T2: write(X)     # X = 40
T1: read(X)      # T1 sees 40
T1: sum = sum + X
T1: read(Y)      # Y = 50 (T2 has not added yet)
T1: !sum = sum + Y   # sum = 190 ✗ (true total is 200 either before or after T2)
T2: read(Y)
T2: Y = Y + 10
T2: write(Y)
''', cap='Incorrect Summary problem (T1 computes a total while T2 moves 10 from X to Y). A = 100, X = 50, Y = 50.')

# ---------------------------------------------------------------- Section 6 conflict serializability
S('swap_rr_1', '''
T1: read(A)
T2: read(A)
''', cap='S1')
S('swap_rr_2', '''
T2: read(A)
T1: read(A)
''', cap='S2 (after swapping)')
S('swap_rw_1', '''
T1: read(A)
T2: write(A)
''', cap='S1')
S('swap_rw_2', '''
T2: write(A)
T1: read(A)
''', cap='S2 (after swapping)')

S('cs1', '''
T1: read(A)
T1: write(A)
T2: read(A)
T2: write(A)
T1: *read(B)
T1: *write(B)
T2: read(B)
T2: write(B)
''', cap='Schedule S (concurrent)', gcap='Precedence graph of S')

S('cs1_step1', '''
T1: read(A)
T1: write(A)
T1: *read(B)
T2: read(A)
T2: write(A)
T1: write(B)
T2: read(B)
T2: write(B)
''', cap='After swaps 1 & 2: read(B) of T1 moved above read(A), write(A) of T2')

S('cs1_final', '''
T1: read(A)
T1: write(A)
T1: read(B)
T1: *write(B)
T2: read(A)
T2: write(A)
T2: read(B)
T2: write(B)
''', cap='After swaps 3 & 4: serial schedule T1 → T2')

S('cs2', '''
T1: read(A)
T2: read(A)
T2: write(A)
T2: read(B)
T1: write(A)
T1: read(B)
T1: write(B)
T2: write(B)
''', cap='Schedule to test', gcap='Precedence graph')

S('t346', '''
T3: read(Q)
T4: write(Q)
T3: write(Q)
T6: write(Q)
''', cap='Schedule with blind writes', gcap='Precedence graph')

S('pg1', '''
T1: read(A)
T2: read(B)
T1: write(A)
T2: write(A)
''', cap='Example 1', gcap='Graph: single edge T1 → T2')

S('pg2', '''
T1: read(A)
T2: read(A)
T1: write(A)
T2: write(A)
''', cap='Example 2', gcap='Graph: cycle T1 ⇄ T2')

S('pg3', '''
T1: read(A)
T1: write(A)
T2: read(A)
T2: write(A)
T1: read(B)
T2: write(B)
''', cap='Example 3', gcap='Graph: all conflicts point the same way')

S('pdfpg', '''
T1: read(A)
T2: read(B)
T1: A := f1(A)
T3: read(C)
T2: B := f2(B)
T2: write(B)
T3: C := f3(C)
T3: write(C)
T1: write(A)
T3: read(B)
T2: read(A)
T2: A := f4(A)
T1: read(C)
T2: write(A)
T1: C := f5(C)
T1: write(C)
T3: B := f6(B)
T3: write(B)
''', cap='Schedule S1 (three transactions)', gcap='Precedence graph of S1 (cycle in red)')

S('lec4', '@R1(A), R2(B), W3(A), R4(C), W1(B), R2(A), W4(B), W3(C), R1(C), W2(C), R4(A), W1(A), R3(B), W4(C), W2(B)',
  cap='Class exercise: R1(A), R2(B), W3(A), R4(C), W1(B), R2(A), W4(B), W3(C), R1(C), W2(C), R4(A), W1(A), R3(B), W4(C), W2(B)',
  gcap='Precedence graph (edges on cycles in red)')

S('acyc3', '''
T1: read(A)
T2: read(B)
T1: write(A)
T3: read(A)
T2: write(B)
T3: read(B)
T3: write(C)
''', cap='Another example', gcap='Precedence graph — acyclic')

# ---------------------------------------------------------------- view serializability
S('vi1', '''
T1: read(A)
T2: write(A)
''', cap='S1')
S('vi2', '''
T2: write(A)
T1: read(A)
''', cap='S2')
S('vu1', '''
T1: write(A)
T2: write(A)
T3: read(A)
''', cap='S1')
S('vu2', '''
T2: write(A)
T1: write(A)
T3: read(A)
''', cap='S2')
S('vf1', '''
T1: write(A)
T2: read(A)
T3: write(A)
''', cap='S1')
S('vf2', '''
T2: read(A)
T1: write(A)
T3: write(A)
''', cap='S2')

S('t346_serial', '''
T3: read(Q)
T3: write(Q)
T4: write(Q)
T6: write(Q)
''', cap='Serial schedule ⟨T3, T4, T6⟩')

S('wt1', '''
T1: write(t)
T2: write(t)
T1: write(t)
''', cap='S: w1(t), w2(t), w1(t)', gcap='Precedence graph of S')
S('wt2', '''
T2: write(t)
T1: write(t)
T1: write(t)
''', cap="Serial ⟨T2, T1⟩")

S('vsno', '@w1(X), r2(X), w2(X), w1(X)', cap='S: w1(X), r2(X), w2(X), w1(X)', gcap='Precedence graph')

# ---------------------------------------------------------------- recoverability
S('nonrec', '''
T8: read(A)
T8: write(A)
T9: read(A)       # T9 reads A written by T8 (uncommitted)
T9: *commit        # T9 commits FIRST
T8: read(B)
T8: !failure → abort   # T8 must be undone, but T9 is already committed — cannot undo T9
''', cap='Non-recoverable schedule')

S('rec', '''
T8: read(A)
T8: write(A)
T9: read(A)       # dirty read (allowed in a recoverable schedule)
T8: read(B)
T8: *commit       # writer commits first …
T9: *commit       # … reader commits after → recoverable
''', cap='Recoverable schedule (T9 delays its commit until T8 commits)')

S('cascade', '''
T1: read(A)
T1: read(B)
T1: write(A)
T2: read(A)      # reads T1's uncommitted A
T2: write(A)
T3: read(A)      # reads T2's uncommitted A
T1: !failure → abort   # T1 rolls back ⇒ T2 must roll back ⇒ T3 must roll back
''', cap='Cascading rollback')

S('cascadeless', '''
T1: read(A)
T1: read(B)
T1: write(A)
T1: *commit
T2: read(A)     # reads only committed data
T2: write(A)
T2: *commit
T3: read(A)
''', cap='Cascadeless schedule (each read happens after the writer commits)')

S('nostrict', '''
T1: read(A)
T1: write(A)
T2: !write(A)    # blind write over T1's UNCOMMITTED value
T1: commit
T2: commit
''', cap='Cascadeless but NOT strict')

# ---------------------------------------------------------------- locking
S('lockbad', '''
T1: lock-X(B)
T1: read(B)          # B = 200
T1: B = B − 50
T1: write(B)         # B = 150
T1: unlock(B)
T2: lock-S(A)
T2: read(A)          # A = 100
T2: unlock(A)
T2: lock-S(B)
T2: read(B)          # B = 150
T2: unlock(B)
T2: !display(A + B)  # shows 250 ✗ (correct total is 300)
T1: lock-X(A)
T1: read(A)
T1: A = A + 50
T1: write(A)         # A = 150
T1: unlock(A)
''', cap='Locking without rules is not enough (A = 100, B = 200; T1 moves 50 from B to A; T2 prints A + B)')

S('deadlock1', '''
T1: lock-X(A)
T1: read(A)
T1: A = A − 50
T1: write(A)
T2: lock-S(B)
T2: read(B)
T2: !lock-S(A)    # WAIT — T1 holds X-lock on A
T1: !lock-X(B)    # WAIT — T2 holds S-lock on B  ⇒ DEADLOCK
''', cap='Deadlock under simple locking (class example)')

S('starve', '''
T1: lock-S(A)     # granted
T2: !lock-X(A)    # must wait (S and X incompatible)
T3: lock-S(A)     # granted (S compatible with T1's S)
T1: unlock(A)
T4: lock-S(A)     # granted (compatible with T3's S)
T3: unlock(A)
T5: lock-S(A)     # granted …
T2: !(still waiting)   # T2 STARVES although the system keeps running
''', cap='Starvation of T2')

S('twopl', '''
T1: lock-S(A)        # growing phase
T1: read(A)
T1: *lock-X(B)       # last lock acquired = LOCK POINT of T1
T1: read(B)
T1: write(B)
T1: unlock(A)        # shrinking phase starts
T2: lock-S(B)        # waits (T1 holds X on B)
T1: commit
T1: unlock(B)
T2: lock-S(B)        # now granted
T2: read(B)
T2: *lock-X(A)       # lock point of T2
T2: write(A)
T2: unlock(B)
T2: unlock(A)
''', cap='Both transactions follow 2PL (class example)')

S('twopl_nonrec', '''
T1: lock-X(A)
T1: write(A)
T1: unlock(A)       # allowed in basic 2PL (T1 is in its shrinking phase)
T2: lock-S(A)
T2: !read(A)        # reads uncommitted value of T1
T2: *commit
T1: commit          # if T1 had aborted here, T2 could not be undone
''', cap='Basic 2PL but not strict — can give dirty reads / non-recoverable schedules')

S('strict', '''
T1: lock-S(A)
T1: read(A)
T1: lock-X(B)
T1: read(B)
T1: write(B)
T1: unlock(A)       # S-lock released early — allowed in strict 2PL
T2: lock-S(A)
T2: read(A)
T1: commit
T1: *unlock(B)      # X-lock released only AFTER commit
T2: lock-S(B)
T2: read(B)
T2: unlock(A)
T2: unlock(B)
T2: commit
''', cap='Schedule under Strict 2PL (corrected class example)')

S('strictdead', '''
T1: lock-X(A)
T2: lock-X(B)
T1: read(A)
T2: read(B)
T1: !lock-X(B)    # waits for T2
T2: !lock-X(A)    # waits for T1 ⇒ DEADLOCK (even under strict 2PL)
''', cap='Strict 2PL can still deadlock')

S('rigorous', '''
T1: lock-S(A)
T1: read(A)
T2: lock-S(A)     # granted (S–S compatible)
T2: read(A)
T1: lock-X(B)
T1: read(B)
T1: write(B)
T2: lock-S(B)     # waits — T1 holds X(B)
T1: *commit
T1: unlock(A)
T1: unlock(B)     # ALL locks released only after commit
T2: lock-S(B)     # granted now
T2: read(B)
T2: *commit
T2: unlock(A)
T2: unlock(B)
''', cap='Schedule under Rigorous 2PL — serialization order = commit order (T1 → T2)')

S('conservative', '''
T1: *lock-X(A), lock-X(B)   # acquires its whole lock set before starting
T1: read(A)
T2: lock-X(A), lock-X(B)    # cannot get ALL locks → waits holding NOTHING
T1: write(A)
T1: read(B)
T1: write(B)
T1: unlock(A), unlock(B)
T2: *lock-X(A), lock-X(B)   # now gets both locks at once
T2: read(B)
T2: write(B)
T2: read(A)
T2: write(A)
T2: unlock(B), unlock(A)
''', cap='Conservative 2PL — no circular wait is possible')

S('lockq_dead', '''
T1: lock-X(A)
T1: read(A)
T1: write(A)
T2: lock-X(B)
T2: read(B)
T2: write(B)
T1: !lock-X(B)    # waits for T2
T2: !lock-X(A)    # waits for T1 ⇒ deadlock
''', cap='Concurrent execution of the two 2PL transactions that deadlocks')

S('pyq_e4_dead', '''
T1: lock-S(X)
T1: read(X)
T2: lock-S(Y)
T2: read(Y)
T2: lock-S(Z)
T2: read(Z)
T1: !lock-X(Y)     # waits — T2 holds S(Y)
T2: !lock-X(X)     # waits — T1 holds S(X)  ⇒ DEADLOCK
''', cap='A possible execution of the locked T1 and T2 that deadlocks')

S('p23_nonser', '''
T1: read(A)                   # A = 0
T2: read(B)                   # B = 0
T1: read(B)                   # B = 0
T2: read(A)                   # A = 0
T1: if A = 0 then B := B + 1  # B = 1
T1: write(B)
T2: if B = 0 then A := A + 1  # T2 had read B = 0 → A = 1
T2: !write(A)                 # final A = 1, B = 1 ✗ violates A = 0 ∨ B = 0
''', cap='A concurrent execution of T1 and T2 that is not serializable')

S('p22_log', '''
T1: read(A)
T2: read(B)
T3: read(C)
T1: write(A)
T2: write(A)
T3: write(B)
T2: write(B)
T1: write(C)
''', cap='Given schedule')

S('deadlock_student', '''
T1: lock-X(Student row)
T2: lock-X(Grade row)
T1: update Student …
T2: update Grade …
T1: !lock-X(Grade row)     # waits for T2
T2: !lock-X(Student row)   # waits for T1 ⇒ deadlock
''', cap='Deadlock between two tables (PDF example)')

# ---------------------------------------------------------------- PYQ schedules
S('p24_s1', '@r1(X); r3(Y); r3(X); r2(Y); r2(Z); w3(Y); w2(Z); r1(Z); w1(X); w1(Z)', cap='S1', gcap='Precedence graph of S1')
S('p24_s2', '@r1(X); r3(Y); r2(Y); r3(X); r1(Z); r2(Z); w3(Y); w1(X); w2(Z); w1(Z)', cap='S2', gcap='Precedence graph of S2 (cycle edges in red)')

S('p25', '@w3(A), r1(A), r5(C), w1(B), r2(B), w2(B), r4(B), w4(B), w3(C), r1(C), w2(C), r6(D), w5(D), r3(D), w6(B), r2(A), w2(A), r4(A), w4(A), r5(B), w5(B), r6(C), w6(C), r1(B), w1(D), r3(B), w3(B), r2(D), w2(D), r4(C), w4(C), r5(A), w5(A), r6(B), w6(A)',
  cap='Schedule S', gcap='Precedence graph of S (every edge lies on a cycle)')

S('p26', '@r1(X); r2(Y); w1(X); r3(X); w2(Y); r1(Y); w3(X); c2; c1; c3', cap='Given schedule', gcap='Precedence graph')

S('pu_s1', '@r1(X); r2(Z); r1(Z); r3(X); r3(Y); w1(X); c1; w3(Y); c3; r2(Y); w2(Z); w2(Y); c2', cap='S1', gcap='Precedence graph of S1')
S('pu_s2', '@r1(X); r2(Z); r1(Z); r3(X); r3(Y); w1(X); w3(Y); r2(Y); w2(Z); w2(Y); c1; c2; c3', cap='S2', gcap='Precedence graph of S2')
S('pu_s3', '@r1(X); r2(Z); r3(X); r1(Z); r2(Y); r3(Y); w1(X); c1; w2(Z); w3(Y); w2(Y); c3; c2', cap='S3', gcap='Precedence graph of S3')

S('p22_s1', '@R1(X), R2(Y), R3(Y), W2(Y), W1(X), W3(X), R2(X), W2(X)', cap='S1', gcap='Precedence graph of S1')

S('m21', '@r1(A); r2(A); r2(B); w2(B); r1(B); w1(A)', cap='Given schedule', gcap='Precedence graph')
S('m21_serial', '@r2(A); r2(B); w2(B); r1(A); r1(B); w1(A)', cap='Equivalent serial schedule ⟨T2, T1⟩')

# ---------------------------------------------------------------- practice set
S('pr1', '@R1(A), W1(A), R2(A), W2(A), R3(B), W3(B)', cap='Practice 1', gcap='Precedence graph')
S('pr2', '@R1(A), R2(B), W1(A), R3(A), W2(B), W3(A)', cap='Practice 2', gcap='Precedence graph')
S('pr3', '@R1(A), W1(A), R2(A), W2(A), R2(B), W2(B), R1(B), W1(B)', cap='Practice 3', gcap='Precedence graph')
S('pr4', '@r1(X); w1(X); r2(X); w2(X); c2; c1', cap='Practice 4')
S('pr5', '@r1(X); w1(X); r2(Y); c1; r2(X); w2(X); c2', cap='Practice 5')
S('pr6', '@r1(A); r2(A); w1(A); w2(A); c1; c2', cap='Practice 6', gcap='Precedence graph')
