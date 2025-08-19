import os
from telethon import TelegramClient

api_id = 21886361
api_hash = 'e86b9347ac72aac313460d941b078a2e'
bot_token = os.environ['TELEGRAM_BOT_TOKEN']  # Fetch bot token from environment
target_bot = '@btt5bot'
session_name = 'mybot_session'

# Create client
client = TelegramClient(session_name, api_id, api_hash).start(bot_token=bot_token)

# The rest of your code...# -*- coding: utf-8 -*-
import asyncio
from telethon import TelegramClient, errors, events
from telethon.tl.types import Channel
import sys
import time

# Your credentials - يجب عليك تعديل هذه القيم
api_id = 21886361
api_hash = 'e86b9347ac72aac313460d941b078a2e'
phone = None  # Will be requested on first run
target_bot = '@btt5bot'  # Target bot to receive links (you can change this)
session_name = 'mybot_session'

# Create client
client = TelegramClient(session_name, api_id, api_hash)

# Global variables to track bot response and forwarding
bot_responded = False
last_bot_message = None
target_channel = None
enable_forwarding = False
files_processed_count = 0
file_process_batch_size = 100
idle_wait_time = 900 # 15 minutes in seconds

async def main():
    """Main program function"""
    global target_channel, enable_forwarding, files_processed_count

    # Connect and login
    await client.start()
    print("=" * 50)
    print("Successfully logged in!")
    print("=" * 50)

    # Get user info
    me = await client.get_me()
    name = me.first_name if me.first_name else "User"
    print(f"Welcome {name}!")
    print("-" * 50)

    # Setup event handler for bot responses
    @client.on(events.NewMessage(from_users=target_bot))
    async def bot_response_handler(event):
        global bot_responded, last_bot_message, original_file_name
        # Check if the new message has media
        if event.message.media:
            bot_responded = True
            last_bot_message = event.message

            # Forward to target channel if enabled
            if enable_forwarding and target_channel:
                try:
                    # Forward the file with original filename as caption
                    if 'original_file_name' in globals() and original_file_name:
                        # Forward with custom caption containing original filename
                        await event.message.forward_to(target_channel)
                        # Then edit the forwarded message to add caption
                        try:
                            # Get the last message (the forwarded one)
                            async for msg in client.iter_messages(target_channel, limit=1):
                                if msg.media:
                                    await client.edit_message(target_channel, msg.id, f"📄 {original_file_name}")
                                break
                        except:
                            pass  # If editing fails, just continue
                    else:
                        # Forward without caption if no filename
                        await client.forward_messages(target_channel, event.message)
                    print(f"✅ File forwarded to {target_channel.title} (Original: {original_file_name if 'original_file_name' in globals() else 'Unknown'})")
                except Exception as e:
                    print(f"❌ Failed to forward file: {e}")

    # Main loop
    while True:
        print("\nOPTIONS:")
        print("1. Process new channel")
        print("2. Configure auto-forwarding")
        print("3. Exit")

        choice = input("\nEnter option number: ").strip()

        if choice == '3':
            print("\nGoodbye!")
            break
        elif choice == '1':
            await process_channel()
        elif choice == '2':
            await configure_forwarding()
        else:
            print("Invalid option!")

async def configure_forwarding():
    """Configure auto-forwarding settings"""
    global target_channel, enable_forwarding

    print("\n" + "=" * 50)
    print("AUTO-FORWARDING CONFIGURATION")
    print("=" * 50)

    print("Current settings:")
    print(f"Auto-forwarding: {'Enabled' if enable_forwarding else 'Disabled'}")
    print(f"Target channel: {target_channel.title if target_channel else 'Not set'}")

    print("\nOptions:")
    print("1. Enable auto-forwarding")
    print("2. Disable auto-forwarding")
    print("3. Change target channel")
    print("4. Back to main menu")

    choice = input("\nEnter option: ").strip()

    if choice == '1':
        if not target_channel:
            channel_input = input("Enter target channel username or link: ").strip()
            if channel_input:
                try:
                    target_channel = await client.get_entity(channel_input)
                    enable_forwarding = True
                    print(f"✅ Auto-forwarding enabled to: {target_channel.title}")
                except Exception as e:
                    print(f"❌ Error: {e}")
            else:
                print("No channel specified!")
        else:
            enable_forwarding = True
            print("✅ Auto-forwarding enabled")

    elif choice == '2':
        enable_forwarding = False
        print("✅ Auto-forwarding disabled")

    elif choice == '3':
        channel_input = input("Enter target channel username or link: ").strip()
        if channel_input:
            try:
                target_channel = await client.get_entity(channel_input)
                print(f"✅ Target channel set to: {target_channel.title}")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("No channel specified!")

async def wait_for_bot_response(timeout=60):
    """Wait for bot to respond with media"""
    global bot_responded
    bot_responded = False

    start_time = time.time()
    while not bot_responded:
        if time.time() - start_time > timeout:
            return False  # Timeout
        await asyncio.sleep(0.5)  # Check every 0.5 seconds

    return True

# Bot availability check removed - bot only responds to file links, not text messages


async def process_channel():
    """Process a single channel and extract post links"""
    global bot_responded, files_processed_count, idle_wait_time, target_channel, enable_forwarding

    # Always ask for target channel to enable auto-forwarding
    if not target_channel:
        print("\n" + "=" * 50)
        print("إعداد التحويل التلقائي - AUTO-FORWARDING SETUP")
        print("=" * 50)
        channel_input = input("أدخل رابط أو اسم القناة للتحويل إليها - Enter target channel username or link: ").strip()
        if channel_input:
            try:
                target_channel = await client.get_entity(channel_input)
                enable_forwarding = True
                print(f"✅ تم تفعيل التحويل التلقائي إلى: {target_channel.title}")
                print(f"✅ Auto-forwarding enabled to: {target_channel.title}")
            except Exception as e:
                print(f"❌ خطأ في تحديد القناة: {e}")
                print(f"❌ Error setting target channel: {e}")
                return
        else:
            print("❌ لم يتم تحديد قناة. لن يتم التحويل التلقائي.")
            print("❌ No channel specified. Auto-forwarding disabled.")
            enable_forwarding = False

    # Ask about text message forwarding
    print("\n" + "=" * 50)
    print("TEXT MESSAGE FORWARDING")
    print("=" * 50)
    print("Do you want to copy text-only messages to the target channel?")
    print("(Messages without any media files)")
    forward_text_choice = input("Copy text messages? (y/n): ").strip().lower()
    forward_text_messages = (forward_text_choice == 'y')
    
    if forward_text_messages:
        print("✅ Text messages will be copied to target channel")
    else:
        print("❌ Text messages will be ignored")


    # Request channel link or username
    channel_input = input("\nEnter channel link or username to process: ").strip()

    if not channel_input:
        print("No input provided!")
        return

    try:
        # Get channel entity
        print(f"\nSearching for channel: {channel_input}")
        channel = await client.get_entity(channel_input)

        if not isinstance(channel, Channel):
            print("This is not a channel!")
            return

        # Channel title with UTF-8 support
        channel_title = channel.title.encode('utf-8').decode('utf-8')
        print(f"Channel found: {channel_title}")

        # Get participant count safely
        participants = "Not available"
        if hasattr(channel, 'participants_count') and channel.participants_count:
            participants = channel.participants_count
        print(f"Members count: {participants}")

        print("\nCollecting messages with files...")
        print("-" * 50)

        # Collect all messages with files and text-only messages
        messages_with_files = []
        text_only_messages = []
        total_messages = 0
        messages_with_files_count = 0
        text_only_count = 0

        # Iterate through all messages and collect ones with files and text-only
        async for message in client.iter_messages(channel):
            total_messages += 1

            # Check if message has any media/file
            if message.media:
                messages_with_files.append(message)
                messages_with_files_count += 1
            elif message.text and message.text.strip() and forward_text_messages:
                # Text-only message (not empty and not just whitespace)
                text_only_messages.append(message)
                text_only_count += 1
                
            print(f"Scanning: {messages_with_files_count} files, {text_only_count if forward_text_messages else 0} text / {total_messages} messages", end='\r')

        print(f"\nTotal messages: {total_messages}")
        print(f"Messages with files: {messages_with_files_count}")
        if forward_text_messages:
            print(f"Text-only messages: {text_only_count}")

        if not messages_with_files and not (forward_text_messages and text_only_messages):
            print("No messages to process found!")
            return

        # Reverse the list to start from oldest
        messages_with_files.reverse()

        # Ask for starting position
        print("\n" + "=" * 50)
        print("START POSITION OPTIONS:")
        print(f"Total messages with files: {messages_with_files_count}")
        print("\nOptions:")
        print("1. Enter message number (1 to {})".format(messages_with_files_count))
        print("2. Enter message link (https://t.me/...)")
        print("3. Press Enter to start from beginning")
        print("=" * 50)

        start_input = input("\nStart from (number/link/Enter): ").strip()

        start_index = 0  # Default start from beginning
        if start_input.isdigit():
            start_num = int(start_input)
            if 1 <= start_num <= messages_with_files_count:
                start_index = start_num - 1
                print(f"Starting from message #{start_num}")
            else:
                print(f"Invalid number! Starting from beginning")
        elif start_input.startswith("https://t.me/"):
            # Extract message ID from link
            try:
                message_id = int(start_input.split('/')[-1])
                
                # First, get the actual message from channel to verify it exists
                try:
                    target_message = await client.get_messages(channel, ids=message_id)
                    if target_message and not target_message.empty:
                        # Find messages with files that come after this message ID
                        found_index = -1
                        for idx, msg in enumerate(messages_with_files):
                            if msg.id >= message_id:
                                found_index = idx
                                break
                        
                        if found_index >= 0:
                            start_index = found_index
                            print(f"Starting from message ID {message_id} or next available file (position #{start_index + 1})")
                            print(f"Note: Will start from first file message at or after message {message_id}")
                        else:
                            print(f"No file messages found after message ID {message_id}! Starting from beginning")
                    else:
                        print(f"Message ID {message_id} not found in channel! Starting from beginning")
                except Exception as get_msg_error:
                    print(f"Could not verify message ID {message_id}: {get_msg_error}")
                    print("Starting from beginning")
            except (ValueError, IndexError):
                print("Invalid link format! Starting from beginning")
        else:
            print("Starting from beginning")

        # Ask for ending position
        print("\nEND POSITION OPTIONS:")
        print(f"Enter ending message number ({start_index + 1} to {messages_with_files_count})")
        print("Or press Enter to process all remaining messages")

        end_input = input("\nEnd at message number: ").strip()

        end_index = messages_with_files_count  # Default process all
        if end_input.isdigit():
            end_num = int(end_input)
            if start_index + 1 <= end_num <= messages_with_files_count:
                end_index = end_num
                print(f"Ending at message #{end_num}")
            else:
                print(f"Invalid number! Processing all remaining messages")
        else:
            print("Processing all remaining messages")

        # Calculate total to process
        total_to_process = end_index - start_index
        print(f"\nWill process {total_to_process} messages (#{start_index + 1} to #{end_index})")

        # Ask for wait method
        print("\nWait method:")
        print("1. Wait for bot response (recommended)")
        print("2. Fixed 30 seconds wait")
        wait_choice = input("\nChoose wait method (1 or 2): ").strip()

        wait_for_response = (wait_choice == '1')

        timeout = 60  # Default timeout
        if wait_for_response:
            timeout_input = input("Enter timeout in seconds (default 60): ").strip()
            timeout = int(timeout_input) if timeout_input.isdigit() else 60

        # Show forwarding status
        print(f"\nAuto-forwarding: {'✅ Enabled' if enable_forwarding and target_channel else '❌ Disabled'}")
        if enable_forwarding and target_channel:
            print(f"Files will be forwarded to: {target_channel.title}")

        # Confirmation prompt
        print("\n" + "=" * 50)
        print("SUMMARY:")
        print(f"Channel: {channel_title}")
        print(f"Processing messages: #{start_index + 1} to #{end_index}")
        print(f"Total to process: {total_to_process}")
        print(f"Wait method: {'Bot response' if wait_for_response else 'Fixed 30s'}")
        if wait_for_response:
            print(f"Timeout: {timeout} seconds")
        print(f"Auto-forwarding: {'Enabled' if enable_forwarding and target_channel else 'Disabled'}")
        print("=" * 50)

        confirm = input("\nContinue? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Operation cancelled")
            return

        print(f"\nSending links (oldest to newest)...")
        print("-" * 50)

        # Counter for sent links and failed operations
        count = 0
        failed_count = 0
        forwarding_failed_count = 0
        skipped_count = start_index
        failed_links = []  # Store failed links
        
        # Bot availability check removed - proceeding directly to file processing

        # Process selected range of messages
        for idx, message in enumerate(messages_with_files[start_index:end_index], 1):
            actual_position = start_index + idx

            # Build message link
            if channel.username:
                link = f"https://t.me/{channel.username}/{message.id}"
            else:
                channel_id = str(channel.id).replace('-100', '')
                link = f"https://t.me/c/{channel_id}/{message.id}"
                
            # Extract file name for logging and store as global for bot handler
            global original_file_name
            original_file_name = "Unknown File"
            
            # Try to get filename from document attributes first
            if message.document and hasattr(message.document, 'file_name') and message.document.file_name:
                original_file_name = message.document.file_name
            # Try to extract filename from message text if available
            elif message.text and any(ext in message.text.lower() for ext in ['.pdf', '.doc', '.txt', '.zip', '.rar', '.mp4', '.mp3', '.jpg', '.png']):
                # Look for filename patterns in the message text
                import re
                # Pattern to match filenames with extensions
                filename_pattern = r'([^\s\/\\]+\.[a-zA-Z0-9]{2,4})'
                matches = re.findall(filename_pattern, message.text)
                if matches:
                    original_file_name = matches[0]  # Take the first match
                else:
                    original_file_name = message.text.strip()[:50] + "..." if len(message.text.strip()) > 50 else message.text.strip()
            # Try to get from document mime_type
            elif message.document and hasattr(message.document, 'mime_type'):
                mime_type = message.document.mime_type
                if 'pdf' in mime_type:
                    original_file_name = f"document_{message.id}.pdf"
                elif 'word' in mime_type or 'msword' in mime_type:
                    original_file_name = f"document_{message.id}.doc"
                elif 'text' in mime_type:
                    original_file_name = f"document_{message.id}.txt"
                elif 'zip' in mime_type:
                    original_file_name = f"document_{message.id}.zip"
                elif 'video' in mime_type:
                    original_file_name = f"document_{message.id}.mp4"
                elif 'audio' in mime_type:
                    original_file_name = f"document_{message.id}.mp3"
                elif 'image' in mime_type:
                    original_file_name = f"document_{message.id}.jpg"
                else:
                    original_file_name = f"document_{message.id}"
            elif message.document:
                original_file_name = f"document_{message.id}"
            elif message.photo:
                original_file_name = f"photo_{message.id}.jpg"
            elif message.video:
                original_file_name = f"video_{message.id}.mp4"

            file_name = original_file_name
            link_processing_failed = False
            forwarding_failed = False

            try:
                # Determine file type
                file_type = "File"
                if message.photo:
                    file_type = "Photo"
                elif message.video:
                    file_type = "Video"
                elif message.document:
                    file_type = "Document"
                elif message.audio:
                    file_type = "Audio"
                elif message.voice:
                    file_type = "Voice"
                elif message.sticker:
                    file_type = "Sticker"
                elif message.gif:
                    file_type = "GIF"

                # Send link to target bot
                print(f"\n[{actual_position}/{messages_with_files_count}] ({idx}/{total_to_process}) Sending {file_type}: {link} (Name: {file_name})")
                await client.send_message(target_bot, link)
                count += 1

                # Wait based on chosen method
                if wait_for_response:
                    print(f"Waiting for bot response (max {timeout}s)...")
                    response_received = await wait_for_bot_response(timeout)

                    if response_received:
                        print("✅ Bot responded with file!")
                        # Check if forwarding was successful (already handled in event handler)
                        # Small delay to avoid being too fast
                        await asyncio.sleep(2)
                    else:
                        print(f"❌ Bot did not respond within {timeout} seconds")
                        link_processing_failed = True
                        failed_count += 1
                        failed_links.append({
                            'position': actual_position,
                            'link': link,
                            'file_type': file_type,
                            'file_name': file_name,
                            'reason': 'Bot timeout'
                        })
                        # Wait a bit before continuing
                        await asyncio.sleep(5)
                else:
                    # Fixed wait time
                    print("Waiting 30 seconds...")
                    await asyncio.sleep(30)

                # Check for batch processing and idle wait
                files_processed_count += 1
                if files_processed_count % file_process_batch_size == 0:
                    print(f"\n🔄 Processed {files_processed_count} files. Pausing for {idle_wait_time // 60} minutes...")
                    print("⏸️ Taking a break to avoid overloading the bot...")
                    await asyncio.sleep(idle_wait_time)
                    
                    print("✅ Resuming processing after break...")

            except errors.FloodWaitError as e:
                print(f"⏳ Rate limit! Waiting {e.seconds} seconds...")
                await asyncio.sleep(e.seconds)
                # Retry
                try:
                    await client.send_message(target_bot, link)
                    count += 1
                    if wait_for_response:
                        response_received = await wait_for_bot_response(timeout)
                        if not response_received:
                            link_processing_failed = True
                            failed_count += 1
                            failed_links.append({
                                'position': actual_position,
                                'link': link,
                                'file_type': file_type,
                                'file_name': file_name,
                                'reason': 'Bot timeout after retry'
                            })
                    else:
                        await asyncio.sleep(30)
                except Exception as retry_error:
                    print(f"❌ Retry failed: {retry_error}")
                    link_processing_failed = True
                    failed_count += 1
                    failed_links.append({
                        'position': actual_position,
                        'link': link,
                        'file_type': file_type,
                        'file_name': file_name,
                        'reason': f'Retry failed: {str(retry_error)}'
                    })
                    continue

            except Exception as e:
                print(f"❌ Error: {e}")
                link_processing_failed = True
                failed_count += 1
                failed_links.append({
                    'position': actual_position,
                    'link': link,
                    'file_type': file_type,
                    'file_name': file_name,
                    'reason': str(e)
                })
                continue

        # Prepare detailed completion report
        completion_msg = f"""
========== PROCESSING COMPLETED ==========
Channel: {channel_title}
Total posts in channel: {total_messages}
Posts with files: {messages_with_files_count}
Processed range: #{start_index + 1} to #{end_index}
Skipped (before start): {skipped_count}
Successfully processed: {count - failed_count}
Failed processing: {failed_count}
Auto-forwarding: {'Enabled' if enable_forwarding and target_channel else 'Disabled'}
Target bot: {target_bot}
==========================================
        """

        # Add failed links details if any
        if failed_links:
            completion_msg += "\n❌ FAILED PROCESSING LINKS:\n"
            completion_msg += "-" * 40 + "\n"
            for failed in failed_links:
                completion_msg += f"Position #{failed['position']}: {failed['file_type']}\n"
                completion_msg += f"Link: {failed['link']}\n"
                completion_msg += f"File Name: {failed.get('file_name', 'N/A')}\n" # Use .get for safety
                completion_msg += f"Reason: {failed['reason']}\n"
                completion_msg += "-" * 40 + "\n"

        # Send detailed report to Saved Messages
        try:
            await client.send_message('me', completion_msg)
            print("📋 Detailed report sent to Saved Messages")
        except Exception as e:
            print(f"Could not send report to saved messages: {e}")

        print(completion_msg)

        # Process text-only messages if enabled
        if forward_text_messages and text_only_messages and target_channel:
            print(f"\n📝 Processing {len(text_only_messages)} text-only messages...")
            print("-" * 50)
            
            text_messages_sent = 0
            text_failed_count = 0
            
            # Reverse to start from oldest
            text_only_messages.reverse()
            
            for idx, message in enumerate(text_only_messages, 1):
                try:
                    # Send text message to target channel
                    text_content = message.text.strip()
                    if text_content:
                        await client.send_message(target_channel, f"📄 النص الأصلي:\n\n{text_content}")
                        text_messages_sent += 1
                        print(f"[{idx}/{len(text_only_messages)}] ✅ Text message sent: {text_content[:50]}...")
                        
                        # Small delay to avoid spam
                        await asyncio.sleep(1)
                        
                except Exception as e:
                    print(f"[{idx}/{len(text_only_messages)}] ❌ Failed to send text: {e}")
                    text_failed_count += 1
                    
            print(f"\n📝 Text Messages Summary:")
            print(f"Successfully sent: {text_messages_sent}")
            print(f"Failed: {text_failed_count}")

        # Save progress
        print("\n💾 SAVE PROGRESS:")
        print(f"Last processed message: #{end_index}")
        print(f"Next time you can start from: #{end_index + 1}")

        # Show summary
        if failed_links:
            print(f"\n⚠️  {len(failed_links)} links failed processing. Check Saved Messages for details.")

    except ValueError as e:
        print(f"Cannot find channel: {channel_input}")
        print("Check:")
        print("1. Link/username is correct")
        print("2. You are member of private channel")

    except errors.ChannelPrivateError:
        print("Private channel - not a member!")

    except Exception as e:
        print(f"Error: {e}")

async def run():
    """Run the program"""
    try:
        await main()
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        await client.disconnect()
        print("Disconnected")

# Run the program
if __name__ == '__main__':
    # Set UTF-8 encoding
    if sys.platform == 'win32':
        import locale
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

    print("="*50)
    print("Telegram UserBot - Files Link Extractor")
    print("With Auto-Forwarding & Enhanced Error Tracking")
    print("="*50)

    # Check telethon
    try:
        import telethon
        print(f"Telethon version: {telethon.__version__}")
    except ImportError:
        print("ERROR: Telethon not installed!")
        print("Run: pip install telethon")
        sys.exit(1)

    # Run
    try:
        client.loop.run_until_complete(run())
    except Exception as e:
        print(f"Failed to start: {e}")