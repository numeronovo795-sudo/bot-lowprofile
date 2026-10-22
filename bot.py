import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput

# Configuração de Permissões (Intents)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Necessário para gerir membros e atribuir cargos
bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------------------------------------------------
# BOTAO PARA FECHAR A SALA DE TESTE
# -------------------------------------------------------------
class FecharSalaView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Fechar Sala 🔒", style=discord.ButtonStyle.danger, custom_id="btn_fechar_sala")
    async def fechar_sala(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("🗑️ Esta sala de teste será apagada em instantes...", ephemeral=True)
        await interaction.channel.delete(reason=f"Sala fechada por {interaction.user.name}")

# -------------------------------------------------------------
# 1. FORMULÁRIO DE INSCRIÇÃO (LOW PROFILE)
# -------------------------------------------------------------
class RecrutamentoModal(Modal, title="Ficha LOW PROFILE - CS Rank"):
    nick_id = TextInput(
        label="Nick Completo e ID no Free Fire", 
        placeholder="Ex: LOW | Pedro - ID: 123456789", 
        required=True
    )
    plataforma_idade = TextInput(
        label="Idade e Plataforma (Mobile/Emulador)", 
        placeholder="Ex: 18 anos / Mobile (iPhone 11)", 
        required=True
    )
    funcao_estilo = TextInput(
        label="Função no CS e Armas de Preferência", 
        placeholder="Ex: Rushador / UMP e Thompson", 
        required=True
    )
    patente_stars = TextInput(
        label="Patente Atual / Estrelas no CS", 
        placeholder="Ex: Mestre 45★ / Desafiante", 
        required=True
    )
    horarios_exp = TextInput(
        label="Horários Livres e Experiência em Treinos", 
        placeholder="Ex: Noite (19h às 23h) / Jogo x-treino diário", 
        style=discord.TextStyle.paragraph,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        CANAL_STAFF_ID = 1559416483916808272  
        canal_staff = interaction.guild.get_channel(CANAL_STAFF_ID)

        embed = discord.Embed(
            title="📋 Nova Candidatura - LOW PROFILE",
            color=discord.Color.red()
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="👤 Discord", value=interaction.user.mention, inline=True)
        embed.add_field(name="🎮 Nick & ID", value=self.nick_id.value, inline=False)
        embed.add_field(name="📱 Idade & Dispositivo", value=self.plataforma_idade.value, inline=False)
        embed.add_field(name="🎯 Função & Armas", value=self.funcao_estilo.value, inline=False)
        embed.add_field(name="📊 Patente / Estrelas", value=self.patente_stars.value, inline=False)
        embed.add_field(name="⏰ Horários & Experiência", value=self.horarios_exp.value, inline=False)
        embed.set_footer(text=f"ID do Jogador: {interaction.user.id}")

        view = DecisaoStaffView(candidato=interaction.user)
        
        if canal_staff:
            await canal_staff.send(embed=embed, view=view)
            await interaction.response.send_message(
                "✅ Sua ficha foi enviada para a liderança da LOW PROFILE! Aguarde o contacto.", 
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Erro ao localizar o canal de relatórios. Verifique se o bot tem acesso ao canal.", 
                ephemeral=True
            )

# -------------------------------------------------------------
# 2. BOTÕES DA STAFF (APROVAR / RECUSAR + CARGO AUTOMÁTICO)
# -------------------------------------------------------------
class DecisaoStaffView(View):
    def __init__(self, candidato: discord.User):
        super().__init__(timeout=None)
        self.candidato = candidato

    @discord.ui.button(label="Aprovar p/ Teste 🟢", style=discord.ButtonStyle.success)
    async def aprovar(self, interaction: discord.Interaction, button: Button):
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)

        guild = interaction.guild

        CARGO_ID = 1560658384636747937
        cargo = guild.get_role(CARGO_ID)

        member = guild.get_member(self.candidato.id)
        if not member:
            try:
                member = await guild.fetch_member(self.candidato.id)
            except Exception as e:
                print(f"⚠️ Erro ao obter membro: {e}")

        cargo_atribuido = False
        if cargo and member:
            try:
                await member.add_roles(cargo)
                cargo_atribuido = True
                print(f"✅ CARGO APLICADO: {cargo.name} para {member.display_name}")
            except discord.Forbidden:
                print("❌ ERRO DE PERMISSÃO: Abra o link de convite que aparece no terminal e autorize o bot novamente com permissões completas!")
            except Exception as e:
                print(f"❌ Erro ao atribuir cargo: {e}")

        categoria = interaction.channel.category

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            self.candidato: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        canal_teste = await guild.create_text_channel(
            name=f"teste-{self.candidato.name}",
            category=categoria,
            overwrites=overwrites
        )

        msg_cargo = f" e recebeu o cargo **{cargo.name}**" if cargo_atribuido and cargo else ""
        
        await canal_teste.send(
            f"🎉 Parabéns {self.candidato.mention}! Sua ficha foi aprovada por {interaction.user.mention}{msg_cargo}.\n"
            f"Combine aqui o horário da sua partida de teste para a **LOW PROFILE**.",
            view=FecharSalaView()
        )
        await interaction.followup.send(f"✅ Candidato aprovado, sala criada: {canal_teste.mention}", ephemeral=True)

    @discord.ui.button(label="Recusar 🔴", style=discord.ButtonStyle.danger)
    async def recusar(self, interaction: discord.Interaction, button: Button):
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)

        try:
            await self.candidato.send("Agradecemos seu interesse na guilda LOW PROFILE, mas sua ficha não foi aprovada no momento.")
        except:
            pass

        await interaction.followup.send(f"❌ Candidatura de {self.candidato.mention} recusada.", ephemeral=True)

# -------------------------------------------------------------
# 3. PAINEL PRINCIPAL DE RECRUTAMENTO - LOW PROFILE
# -------------------------------------------------------------
class PainelInicialView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📝 Candidatar-se", style=discord.ButtonStyle.primary, custom_id="btn_recrutar")
    async def abrir_modal(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(RecrutamentoModal())

@bot.command()
@commands.has_permissions(administrator=True)
async def painel_recrutamento(ctx):
    embed = discord.Embed(
        title="🔥 RECRUTAMENTO - GUILDA LOW PROFILE 🔥",
        description="Quer fazer parte da **LOW PROFILE** para o CS Ranqueado?\n\n"
                    "📌 **Requisitos básicos:**\n"
                    "• Respeito e boa comunicação\n"
                    "• Foco em evolução nas partidas\n"
                    "• Disponibilidade para treinos e line\n\n"
                    "Clique no botão abaixo para preencher sua ficha de inscrição!",
        color=discord.Color.red()
    )
    embed.set_footer(text="Low Profile Guild • Recrutamento CS")
    await ctx.send(embed=embed, view=PainelInicialView())

# -------------------------------------------------------------
# GERADOR AUTOMÁTICO DO LINK DE CONVITE NO TERMINAL
# -------------------------------------------------------------
@bot.event
async def on_ready():
    # Gera o link oficial com permissão de Administrador (8)
    link_convite = discord.utils.oauth_url(bot.user.id, permissions=discord.Permissions(8))
    print(f"\n==================================================")
    print(f"🤖 Bot LOW PROFILE {bot.user} está ONLINE!")
    print(f"🔗 LINK DE CONVITE COM PERMISSÃO TOTAL:")
    print(f"{link_convite}")
    print(f"==================================================\n")

# -------------------------------------------------------------
# 4. EXECUÇÃO DO BOT
# -------------------------------------------------------------
bot.run("")