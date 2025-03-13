import csv
import sys
import instaloader
import random
import logging

# Suppress instaloader logging messages
logging.getLogger("instaloader").setLevel(logging.CRITICAL)

# Define a silent context to override logging methods
from instaloader import InstaloaderContext

class SilentInstaloaderContext(InstaloaderContext):
    def error(self, msg: str, *args, **kwargs):
        pass
    def log(self, msg: str, *args, **kwargs):
        pass
    def info(self, msg: str, *args, **kwargs):
        pass
    def debug(self, msg: str, *args, **kwargs):
        pass

# Message templates (kept intact with emojis)
t1 = '''Enough is enough, {name}. {posts} posts → {followers} followers = {ratio:.1f} leads/post.
Stop the madness. Your Instagram is a dead zone. Our AI scans Google + Insta for your ideal clients,
auto-sends cold DMs that 48% actually open. No fluff. Just leads. Reply 'YES' and I'll pull 7
leads within a week. Or brother just keep with your calculator and no leads.'''

t2 = '''Wake up, {name}. {posts} posts → {followers} followers = {ratio:.1f} leads/post. Brutal math.
I think you are suffering with low or even no leads conversion for your business. 
My AI crawls Google + Insta, researches 200+ leads/day, and fires DMs so sharp that 48% beg to reply.
You? You're stuck with hashtags and prayers.
Reply 'YES' and I'll hand-deliver 7 agency leads in 7 days.
Or keep chasing your {ratio:.1f} leads/post like a circus monkey. 🔥'''

t3 = '''Wake up, {name}. {posts} posts → {followers} followers.
Your Instagram is just a diary, not a lead machine.
My AI hunts 200+ real agency leads daily on Google/Insta, researches them, and blasts cold DMs that
48% actually open. You? You're still typing 'Hey dear' like an unpaid intern.
Reply 'YES' and I'll dump 7 hot leads in your inbox this week. Or keep pretending
you love wasting 6 hours/day. 🚀'''

# Initialize Instaloader with a silent context
L = instaloader.Instaloader(quiet=True)
silent_ctx = SilentInstaloaderContext()
L.context = silent_ctx

csv_filename = 'gamenext.csv'
chunk_size = 12  # Process 12 leads per run

# Use UTF-8 encoding to support all characters in your templates
with open(csv_filename, 'r+', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    rows = list(reader)
    fieldnames = reader.fieldnames

    processed = 0
    attempt = 0

    for row in rows:
        # Skip rows already processed (marked with 'y' or 'e')
        if row.get('Done ?', '').lower() in ['y', 'e']:
            continue
        if processed >= chunk_size:
            break

        attempt += 1
        link = row.get('Link', '').strip()
        if not link:
            row['Done ?'] = 'e'
            print(f"fail,{attempt}")
            processed += 1
            continue

        try:
            username = link.rstrip('/').split('/')[-1]
            profile = instaloader.Profile.from_username(L.context, username)
            
            row['Name'] = profile.full_name
            row['Username'] = profile.username
            row['Bio'] = profile.biography
            row['Followers'] = profile.followers
            row['Posts'] = profile.mediacount

            profile_data = {
                'name': profile.full_name,
                'posts': profile.mediacount,
                'followers': profile.followers,
                'ratio': profile.followers / profile.mediacount if profile.mediacount > 0 else 0,
                'bio': profile.biography,
            }
            template = random.choice([t1, t2, t3])
            row['Msg'] = template.format(**profile_data)
            row['Done ?'] = 'y'
            print(f"done,{attempt}")
        except Exception:
            row['Done ?'] = 'e'
            print(f"fail,{attempt}")
        processed += 1

    csvfile.seek(0)
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    csvfile.truncate()

print(f"Processing complete. Processed {processed} leads.")
