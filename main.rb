require "mysql2"

Activity = Struct.new(:id, :created_at, :updated_at, :action, :content, :channel_id, :user)
User = Struct.new(:id, :username)

def get_results
    start = Time.now

    client = Mysql2::Client.new(:host => "localhost", :username => "root")
    results = client.query("
    SELECT act.*, usr.id, usr.username
    FROM kandan_lg.activities AS act
    INNER JOIN kandan_lg.users AS usr
        ON act.user_id = usr.id
    ")
    # WHERE LOWER(act.content) LIKE '%win the%'
    ends = Time.now

    results = results.map do |row|
        usr = User.new(row['user_id'], row['username'])
        act = Activity.new(row['id'], row['created_at'], row['updated_at'], row['action'], row['content'].downcase[0..20], row['channel_id'], usr)
    end

    # results.first(10).each do |row|
    #     # conveniently, row is a hash
    #     # the keys are the fields, as you'd expect
    #     # the values are pre-built ruby primitives mapped from their corresponding field types in MySQL
    #     puts(row)
    # end

    # results.each do |row|
    #     row['content'].downcase!
    # end

    puts(ends - start)

    results
end

def run_query(results)
    puts('ruby run query')
    start = Time.now
    query_word = 'win the'.downcase
    out = results.select do |row|
        row.content.include?(query_word)
    end
    ends = Time.now
    puts("#{out.length} #{1000 * (ends - start)}ms")
end

results = get_results
run_query(results)
