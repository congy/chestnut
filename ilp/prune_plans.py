# opt 1: if plan mem cost > mem bound, do not consider
# opt 2: if plan's every ds is not shared with other query, collect all such plans and only keep the best ones
# opt 3: if plan time is too long (how long?), do not consider