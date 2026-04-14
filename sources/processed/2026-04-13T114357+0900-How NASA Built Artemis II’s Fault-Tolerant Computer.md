---
title: "How NASA Built Artemis II’s Fault-Tolerant Computer"
source: "https://cacm.acm.org/news/how-nasa-built-artemis-iis-fault-tolerant-computer/"
author:
  - "[[Logan Kugler]]"
published: 2026-04-09
created: 2026-04-13
description:
tags:
  - "clippings"
url: "https://cacm.acm.org/news/how-nasa-built-artemis-iis-fault-tolerant-computer/"
clipped: "2026-04-13T11:43:57+09:00"
---
The computer system aboard the current Artemis II lunar space mission is from a different world that the one from the Apollo era. Apollo astronauts navigated to the lunar surface using a computer with a 1-MHz processor and roughly 4 kilobytes of erasable memory, supported by a larger store of fixed “rope” memory. While it was a marvel of 1960s engineering, the Apollo Guidance Computer’s functional scope was focused and not in the control loop for every system. Critical environmental and power controls were managed through manual or electromechanical means, such as switches and relays.

This month’s Artemis II mission carrying a crew of four around the Moon for the first time in over 50 years is supported by one of the most fault-tolerant computer system built for spaceflight. Unlike Apollo, the Orion capsule’s computing architecture manages nearly all of the vessel’s safety-critical functions, from life support to communication routing.

When a mission is 250,000 miles from Earth, failure is unrecoverable. There are no runways for emergency landings and no technicians to swap out a fried motherboard. Every subsystem must be designed to survive cosmic-ray bit flips, radiation-induced latch-ups, and hardware faults without a single second of downtime.

“We still architect to cover for hardware failures,” said Nate Uitenbroek, Software Integration and Verification Lead in NASA’s Orion Program at Johnson Space Center. “Along with physically redundant wires, we have logically redundant network planes. We have redundant flight computers. All this is in place to cover for a hardware failure.”

One of the biggest drivers for this redundancy is the harsh radiation environment of space, where high-energy particles can affect avionics and create ‘wrong answers’ that must be filtered out of the flight solution.

**The Power of Eight**

To ensure those wrong answers never reach the spacecraft’s thrusters, NASA moved beyond the triple redundancy of traditional systems. Orion utilizes two Vehicle Management Computers, each containing two Flight Control Modules, for a total of four FCMs. But the redundancy goes even deeper: each FCM consists of a self-checking pair of processors.

Effectively, eight CPUs run the flight software in parallel. The engineering philosophy hinges on a “fail-silent” design. The self-checking pairs ensure that if a CPU performs an erroneous calculation due to a radiation event, the error is detected immediately and the system responds.

“A faulty computer will fail silent, rather than transmit the ‘wrong answer,’” Uitenbroek explained. This approach simplifies the complex task of the triplex “voting” mechanism that compares results. Instead of comparing three answers to find a majority, the system uses a priority-ordered source selection algorithm among healthy channels that haven’t failed-silent. It picks the output from the first available FCM in the priority list; if that module has gone silent due to a fault, it moves to the second, third, or fourth.

This level of redundancy is specifically scaled for the rigors of deep space. NASA anticipates transient failures during the Artemis II mission’s transit through the high-radiation Van Allen Belts.

“We can lose three FCMs in 22 seconds and still ride through safely on the last FCM,” said Uitenbroek. A silenced FCM doesn’t become dead weight, however; the system is designed to reset, re-synchronize its state with the operating modules, and re-join the group mid-flight.

**Enforcing Determinism**

Running multiple independent computers in lockstep is a notorious challenge in computer science, as slight timing drifts or processor variances can cause healthy computers to appear to diverge. NASA solves this through a strictly deterministic architecture.

This architectural discipline is increasingly rare in modern development. Michael Riley, a team lead at Carnegie Mellon’s Software Engineering Institute who previously collaborated with NASA to adapt risk-assessment tools for the Orion mission, noted that while earlier generations worked within strict hardware constraints, modern mission-critical development is different.

“Modern Agile and DevOps approaches prioritize iteration, which can challenge architectural discipline,” Riley explained. “As a result, technical debt accumulates, and maintainability and system resiliency suffer.”

Orion utilizes a time-triggered Ethernet network where time is distributed across the entire system. The flight software operates within “major frames” divided into “minor frames,” managed by an ARINC653-compliant scheduler. This architecture utilizes time and space partitioning to schedule partitions within these frames, ensuring inputs and outputs are perfectly aligned to the network schedule.

“This architecture ensures that each FCM sees the same inputs, runs the same application code, and produces the same outputs,” said Uitenbroek. Every second, the drift of any individual FCM is measured and its local clock is recalibrated to the network’s ‘true’ time. If an application fails to meet its strict deadline, the module is automatically silenced, reset, and re-synchronized.

The hardware itself is also reinforced. The system employs triple-modular-redundant memory that self-corrects single-bit errors on every read. Even the network interface cards utilize two lanes of traffic that are constantly compared, ensuring that a bit flip in the communication fabric results in a fail-silent event rather than a corrupted command. The network itself is triple redundant with three separate planes, and all network switches employ self-checking strategies.

**The Ultimate Fallback**

While the four-FCM primary system is robust, NASA must still account for common mode failures—software bugs or catastrophic events that could theoretically impact all primary channels simultaneously.

To mitigate this, Orion carries a completely independent Backup Flight Software (BFS) system. This is a prime example of dissimilar redundancy. It is implemented on different hardware, runs a different operating system, and utilizes independently developed, simplified flight software.

“It is intentionally different to ensure that a common mode software failure in the primary flight software isn’t also implemented incorrectly on the backup,” Uitenbroek said. The BFS runs constantly in the background and automatically takes over via source selection if the primary computers fail. If the system finds itself on the BFS, it can complete all dynamic portions of the mission to reach a quiescent phase, at which point the crew can attempt to recover the primary FCMs.

Riley emphasized that while fail-silent logic is critical, it must be paired with active monitoring to avoid catastrophic gaps.

“If a software component fails silently, the failure may go undetected unless monitored by another component or watchdog timer,” he said. For mission assurance, he said, error detection and recovery mechanisms must be explicitly designed and correlated across multiple layers of the codebase to ensure consistent behavior.

Even in a total power loss scenario—called a “dead bus”—Orion is designed to survive. If power is restored, the spacecraft enters a safe mode, in which the vehicle first stabilizes itself and then points its solar arrays at the Sun to recover power. Then, it orients its tail toward the Sun for thermal stability before attempting to re-establish communication with Earth. During such a failure, the crew can also take manual action to configure life support systems or don space suits.

**A Future of Reliability**

The changes from Apollo to Artemis represent a massive leap in software complexity. While Apollo’s AGC was a singular achievement, its mechanical fallbacks meant the computer wasn’t the sole arbiter of the crew’s survival. Today, with software managing every thermal valve and power relay, the challenge is ensuring that the software remains synchronized and valid amidst a barrage of cosmic radiation.

To reach this level of confidence, NASA now employs modern verification workflows. This includes full-environment simulations and Monte Carlo stress testing to model worst-case latencies and communication outages. High-performance supercomputers are used for large-scale fault injection, emulating entire flight timelines where catastrophic hardware failures are introduced to see if the software can successfully ‘fail silent’ and recover.

As spaceflight technology has historically seeded commercial advances, Orion’s zero-tolerance architecture offers a preview of a future where mainstream computing—from autonomous vehicles to industrial grids—can achieve the same always-on resilience that’s required for the stars.

***Logan Kugler*** *is a technology writer specializing in artificial intelligence based in Tampa, FL, USA. He has been a regular contributor to* CACM *for 15 years and has written for nearly 100 major publications.*