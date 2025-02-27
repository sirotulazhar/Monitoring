import streamlit as st
from abc import ABC, abstractmethod

class BaseDashboard(ABC):
    def __init__(self, df):
        self.df = df

    @abstractmethod
    def show_metrics(self):
        pass
    
    def run(self):
        self.show_metrics()
        
