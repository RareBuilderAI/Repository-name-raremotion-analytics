-- Preserve balances and serialize concurrent usage requests.
begin;
create or replace function public.consume_analysis()
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
    current_user_id uuid := auth.uid();
    profile public.profiles%rowtype;
begin
    if current_user_id is null then
        raise exception 'Authentication required' using errcode = '28000';
    end if;
    select * into profile from public.profiles
    where id = current_user_id for update;
    if not found then
        raise exception 'Profile unavailable' using errcode = 'P0002';
    end if;
    if profile.free_analyses_used is null or profile.paid_credits is null
       or profile.free_analyses_used < 0 or profile.paid_credits < 0 then
        raise exception 'Invalid usage counters' using errcode = '22023';
    end if;
    if profile.free_analyses_used < 2 then
        update public.profiles set free_analyses_used = free_analyses_used + 1
        where id = current_user_id;
    elsif profile.paid_credits > 0 then
        update public.profiles set paid_credits = paid_credits - 1
        where id = current_user_id;
    else
        return jsonb_build_object('allowed', false);
    end if;
    return jsonb_build_object('allowed', true);
end;
$$;
revoke all on function public.consume_analysis() from public, anon;
grant execute on function public.consume_analysis() to authenticated;
-- Keep own-profile SELECT. Only the function or trusted administrators may
-- change usage balances; ordinary users cannot reset their own allowance.
revoke insert, update, delete, truncate, references, trigger
on public.profiles from public, anon, authenticated;
notify pgrst, 'reload schema';
commit;
