ZINIT_HOME="${XDG_DATA_HOME:-${HOME}/.local/share}/zinit/zinit.git"

# Automatically download zinit
if [ ! -d "$ZINIT_HOME" ]; then
    mkdir -p "$(dirname $ZINIT_HOME)"
    git clone https://github.com/zdharma-continuum/zinit.git "$ZINIT_HOME"
fi

source "${ZINIT_HOME}/zinit.zsh"

# Plugins

zinit light zsh-users/zsh-syntax-highlighting
zinit light zsh-users/zsh-completions
zinit light zsh-users/zsh-autosuggestions
zinit light Aloxaf/fzf-tab

zinit snippet OMZP::git
zinit snippet OMZP::sudo

source ~/.zsh/keybinds.zsh
source ~/.zsh/colors.zsh

# Load completions
autoload -U compinit && compinit
zinit cdreplay -q

# History
HISTSIZE=5000
HISTFILE=~/.zsh_history
SAVEHIST=10000
setopt share_history
setopt hist_ignore_space
setopt extended_history
setopt hist_expire_dups_first
setopt hist_ignore_dups
setopt hist_verify

# Completion
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'
zstyle ':completion:*' list-colors ${(s.:.)LS_COLORS}
zstyle ':completion:*' special-dirs true
zstyle ':completion:*' menu no
zstyle ':fzf-tab:complete:cd:*' fzf-preview 'ls --color $realpath'
zstyle ':completion:*:cd:*' tag-order local-directories directory-stack path-directories
zstyle ':completion:*' use-cache yes
zstyle ':completion:*' cache-path $ZSH_CACHE_DIR

setopt auto_menu
setopt complete_in_word
setopt always_to_end
setopt autocd

# Aliases
source ~/.aliases

eval "$(zoxide init --cmd cd zsh)"
eval "$(fzf --zsh)"
eval "$(oh-my-posh init zsh --config '~/.p10k.omp.yml')"
#eval "$(~/Dev/oh-my-posh/src/omp init zsh --config '~/.p10k.omp.yml')"

# Created by `pipx` on 2025-08-18 19:52:55
export PATH="$PATH:/home/womax/.local/bin"
