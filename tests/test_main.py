import pytest
from main import regex_to_nfa, nfa_to_dfa, are_equivalent, DFA


def test_equivalent_regex():
    # test 1
    regex1 = "a"
    regex2 = "a"

    nfa1 = regex_to_nfa(regex1)
    nfa2 = regex_to_nfa(regex2)

    dfa1 = nfa_to_dfa(nfa1).minimize()
    dfa2 = nfa_to_dfa(nfa2).minimize()

    assert are_equivalent(dfa1, dfa2)

    # test 2
    regex1 = "(a)"
    regex2 = "a"

    nfa1 = regex_to_nfa(regex1)
    nfa2 = regex_to_nfa(regex2)

    dfa1 = nfa_to_dfa(nfa1).minimize()
    dfa2 = nfa_to_dfa(nfa2).minimize()

    assert are_equivalent(dfa1, dfa2)

    # test 3
    regex1 = "a|b"
    regex2 = "b|a"

    nfa1 = regex_to_nfa(regex1)
    nfa2 = regex_to_nfa(regex2)

    dfa1 = nfa_to_dfa(nfa1).minimize()
    dfa2 = nfa_to_dfa(nfa2).minimize()

    assert are_equivalent(dfa1, dfa2)

    # test 4
    regex1 = "a*b*"
    regex2 = "(a*)(b*)"

    nfa1 = regex_to_nfa(regex1)
    nfa2 = regex_to_nfa(regex2)

    dfa1 = nfa_to_dfa(nfa1).minimize()
    dfa2 = nfa_to_dfa(nfa2).minimize()

    assert are_equivalent(dfa1, dfa2)

    # test 5
    regex1 = "a**"
    regex2 = "a*"

    nfa1 = regex_to_nfa(regex1)
    nfa2 = regex_to_nfa(regex2)

    dfa1 = nfa_to_dfa(nfa1).minimize()
    dfa2 = nfa_to_dfa(nfa2).minimize()

    assert are_equivalent(dfa1, dfa2)

    # test 6
    regex1 = "a(b|c)"
    regex2 = "ab|ac"

    nfa1 = regex_to_nfa(regex1)
    nfa2 = regex_to_nfa(regex2)

    dfa1 = nfa_to_dfa(nfa1).minimize()
    dfa2 = nfa_to_dfa(nfa2).minimize()

    assert are_equivalent(dfa1, dfa2)

    # test 7
    regex1 = "(a*b*)*"
    regex2 = "(a|b)*"

    nfa1 = regex_to_nfa(regex1)
    nfa2 = regex_to_nfa(regex2)

    dfa1 = nfa_to_dfa(nfa1).minimize()
    dfa2 = nfa_to_dfa(nfa2).minimize()

    assert are_equivalent(dfa1, dfa2)

    # test 8
    regex1 = "a(bc)"
    regex2 = "abc"

    nfa1 = regex_to_nfa(regex1)
    nfa2 = regex_to_nfa(regex2)

    dfa1 = nfa_to_dfa(nfa1).minimize()
    dfa2 = nfa_to_dfa(nfa2).minimize()

    assert are_equivalent(dfa1, dfa2)

    # test 9
    regex1 = "((a))"
    regex2 = "a"

    nfa1 = regex_to_nfa(regex1)
    nfa2 = regex_to_nfa(regex2)

    dfa1 = nfa_to_dfa(nfa1).minimize()
    dfa2 = nfa_to_dfa(nfa2).minimize()

    assert are_equivalent(dfa1, dfa2)

    # test 10
    regex1 = "a*b"
    regex2 = "ab*"

    nfa1 = regex_to_nfa(regex1)
    nfa2 = regex_to_nfa(regex2)

    dfa1 = nfa_to_dfa(nfa1).minimize()
    dfa2 = nfa_to_dfa(nfa2).minimize()

    assert not are_equivalent(dfa1, dfa2)

    # test 11
    regex1 = "(a|b)c"
    regex2 = "a|bc"

    nfa1 = regex_to_nfa(regex1)
    nfa2 = regex_to_nfa(regex2)

    dfa1 = nfa_to_dfa(nfa1).minimize()
    dfa2 = nfa_to_dfa(nfa2).minimize()

    assert not are_equivalent(dfa1, dfa2)

    # test 12
    regex1 = "a(b|c)*"
    regex2 = "(ab|ac)*"

    nfa1 = regex_to_nfa(regex1)
    nfa2 = regex_to_nfa(regex2)

    dfa1 = nfa_to_dfa(nfa1).minimize()
    dfa2 = nfa_to_dfa(nfa2).minimize()

    assert not are_equivalent(dfa1, dfa2)


def test_invalid_regex():
    with pytest.raises(Exception):
        regex_to_nfa("a|b(c")
