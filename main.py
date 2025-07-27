from functions.create_files import create_files
from utils.db_api_async.db_init import init_db
from functions.activity import add_wallets_db, process_tasks
import os
import sys
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def print_logo():
    panel = Panel(
        "[bold white]PLUME FARMER 1.0[/bold white]\n\n"
        "GitHub: [link]https://github.com/Buldozerch[/link]\n"
        "Channel: [link]https://t.me/buldozercode[/link]",
        width=60,
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(panel)
    console.print()


def print_menu():
    menu = Table(show_header=False, box=None)
    menu.add_column("Option", style="cyan")
    menu.add_column("Description", style="white")

    menu.add_row("1)", "Import wallets in Data Base")
    menu.add_row("2)", "Main process for all wallets")
    menu.add_row("3)", "Register Account in Plume Portal")
    menu.add_row("4)", "Bridge ETH from ARB/OP/BASE to Plume")
    menu.add_row("5)", "Wrap and Unwrap Plume")
    menu.add_row("6)", "Withdraw from Plume and Send to Exchange Wallet")
    menu.add_row("7)", "Exit")

    console.print(menu)


async def main():
    create_files()
    await init_db()
    while True:
        os.system("cls" if os.name == "nt" else "clear")  # Очищаем консоль
        print_logo()
        print_menu()

        try:
            action = input("\n> ")

            if action == "1":
                console.print("\n[bold cyan]Import wallets in DB...[/]")
                await add_wallets_db()
                console.print(
                    "[bold green]Import success. Press Enter to continue...[/]"
                )
                input()

            elif action == "2":
                console.print("\n[bold cyan]Start main process.[/]")
                await process_tasks(specific_task="main")
                console.print(
                    "[bold green]Main process done. Press Enter to continue...[/]"
                )
                input()

            elif action == "3":
                console.print("\n[bold cyan]Start Register process.[/]")
                await process_tasks(specific_task="register")
                console.print(
                    "[bold green]Register process done. Press Enter to continue...[/]"
                )
                input()

            elif action == "4":
                console.print("\n[bold cyan]Start ETH Bridge to Plume.[/]")
                await process_tasks(specific_task="bridge")
                console.print("[bold green]Bridge done. Press Enter to continue...[/]")
                input()

            elif action == "5":
                console.print("\n[bold cyan]Start Wrap/Unwrap activity.[/]")
                await process_tasks(specific_task="swap")
                console.print(
                    "[bold green]Wrap/Unwrap done. Press Enter to continue...[/]"
                )
                input()

            elif action == "6":
                console.print("\n[bold cyan]Start Withdraw activity.[/]")
                await process_tasks(specific_task="swap")
                console.print(
                    "[bold green]Withdraw done. Press Enter to continue...[/]"
                )
                input()

            elif action == "7":
                console.print("\n[bold cyan]Exit.[/]")
                sys.exit(0)

        except KeyboardInterrupt:
            console.print("\n[bold cyan]Exit.[/]")
            sys.exit(0)
        except ValueError as err:
            console.print(f"\n[bold red]Wrong with input data: {err}[/]")
            input("Press Enter to continue...")
        except Exception as e:
            console.print(f"\n[bold red]Error: {e}[/]")
            input("Press Enter to continue...")


if __name__ == "__main__":
    asyncio.run(main())
